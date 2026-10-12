# NVIDIA GPU Administration on Windows 11

## Prerequisites

```powershell
# Verify nvidia-smi is accessible
where.exe nvidia-smi
# Default path: C:\Windows\System32\nvidia-smi.exe
# Or: C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe

# Add to PATH if needed
$nvPath = "C:\Program Files\NVIDIA Corporation\NVSMI"
[System.Environment]::SetEnvironmentVariable('PATH',
    "$([System.Environment]::GetEnvironmentVariable('PATH','User'));$nvPath", 'User')
```

## Driver information and queries

```powershell
# Driver version, CUDA version, GPU name
nvidia-smi

# Structured query output (easier to parse in scripts)
nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used,memory.free `
    --format=csv,noheader,nounits

# All available query fields
nvidia-smi --help-query-gpu

# GPU utilisation and temperature (one-time)
nvidia-smi --query-gpu=name,utilization.gpu,utilization.memory,temperature.gpu,power.draw `
    --format=csv,noheader

# Continuous monitoring (refresh every 2 seconds)
nvidia-smi dmon -s pucvmet -d 2

# Per-process GPU memory usage
nvidia-smi --query-compute-apps=pid,used_memory,name --format=csv,noheader
```

## Monitoring script

```powershell
#Requires -Version 7.0
<#
.SYNOPSIS
    Continuous GPU metrics logger to CSV.
.PARAMETER OutputPath
    CSV file to append metrics to.
.PARAMETER IntervalSeconds
    Sampling interval (default: 5).
.PARAMETER DurationMinutes
    How long to run. 0 = run until Ctrl+C (default: 0).
#>
param(
    [string]$OutputPath = ".\gpu-metrics.csv",
    [int]$IntervalSeconds = 5,
    [int]$DurationMinutes = 0
)

$header = "Timestamp,GPU,TempC,GPU_Util%,Mem_Util%,MemUsed_MB,MemFree_MB,PowerW,FanSpeed%"
if (-not (Test-Path $OutputPath)) {
    $header | Out-File -FilePath $OutputPath -Encoding utf8
}

$stopAt = if ($DurationMinutes -gt 0) { (Get-Date).AddMinutes($DurationMinutes) } else { $null }

Write-Host "Logging GPU metrics to $OutputPath (Ctrl+C to stop)..."

while ($true) {
    $now = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $raw = nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,utilization.memory,memory.used,memory.free,power.draw,fan.speed `
        --format=csv,noheader,nounits

    foreach ($line in $raw) {
        "$now,$line" | Add-Content -Path $OutputPath -Encoding utf8
    }

    Write-Host "[$now] $($raw -join ' | ')"

    if ($stopAt -and (Get-Date) -ge $stopAt) { break }
    Start-Sleep -Seconds $IntervalSeconds
}
```

## Performance mode configuration

### Via nvidia-smi (preferred method)

```powershell
# Set persistence mode (keeps driver loaded, reduces first-launch latency)
# Note: on Windows this is less relevant than on Linux — driver stays loaded anyway
nvidia-smi -pm 1  # enable; -pm 0 to disable

# Set performance level (P0 = max, P8 = power save)
# Requires admin
nvidia-smi -ac <mem_clock>,<graphics_clock>  # set application clocks
nvidia-smi -rac  # reset to default

# Force max performance state (disables adaptive clocking)
nvidia-smi --auto-boost-default=0
nvidia-smi -pl <watts>  # set power limit (within TDP range)

# Query supported clock speeds
nvidia-smi -q -d SUPPORTED_CLOCKS
```

### Via registry (persistent, survives reboots)

```powershell
# NVIDIA power management: prefer maximum performance
# 0 = Adaptive, 1 = Prefer maximum performance
# Path applies per-GPU — query the GUIDs first
$gpuKeys = Get-ChildItem 'HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}' |
    Where-Object { (Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue).DriverDesc -match 'NVIDIA' }

foreach ($key in $gpuKeys) {
    Set-ItemProperty -Path $key.PSPath -Name 'PerfLevelSrc' -Value 0x2222 -Type DWORD
    # 0x2222 = "prefer maximum performance" for all scenarios
}

# Global NVIDIA power policy (affects all GPUs)
# HKLM:\SYSTEM\CurrentControlSet\Control\Video\{GUID}\0000
# PreferredPState: 0x00000000 = adaptive, 0x00000008 = max performance
```

### Via NVIDIA Control Panel (scriptable via nvcpl.dll)

```powershell
# Power management mode via COM — requires NVIDIA Control Panel installed
$nvcpl = New-Object -ComObject NvCplApi.Application -ErrorAction SilentlyContinue
if ($nvcpl) {
    # 0 = Adaptive, 1 = Max Performance, 2 = Optimal Power
    $nvcpl.SetString(0, "PowerMizerEnable", "1")          # enable power management
    $nvcpl.SetString(0, "PowerMizerLevel", "1")           # 1 = prefer max performance
    $nvcpl.SetString(0, "PowerMizerLevelAC", "1")         # AC power policy
}
# Note: COM interface availability varies by driver version; registry method is more reliable
```

## TDR (Timeout Detection and Recovery)

TDR is Windows' watchdog for GPU hangs. Events 4101 (recovery) and 4117 (error) in the System log
indicate the GPU froze and Windows reset the driver. Common causes: driver bugs, overclocking,
VRAM pressure, power delivery issues.

```powershell
# Check for recent TDR events
Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    Id        = 4101, 4117
    StartTime = (Get-Date).AddDays(-7)
} | Select-Object TimeCreated, Id, Message | Format-List

# Increase TDR delay (default 2 seconds — extend if GPU tasks legitimately need longer)
# WARNING: higher values mean Windows waits longer before recovering a hung system
$tdrPath = 'HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers'
Set-ItemProperty -Path $tdrPath -Name 'TdrDelay' -Value 8 -Type DWORD       # seconds
Set-ItemProperty -Path $tdrPath -Name 'TdrDdiDelay' -Value 10 -Type DWORD   # DDI call timeout

# Disable TDR entirely (only for dedicated GPU compute — dangerous on display GPU)
Set-ItemProperty -Path $tdrPath -Name 'TdrLevel' -Value 0 -Type DWORD
# 0 = disabled, 3 = recover (default), 4 = debug (BSOD on TDR)

# IMPORTANT: reboot required for TDR changes to take effect
```

## CUDA environment setup

```powershell
# Verify CUDA is available
nvcc --version       # CUDA compiler
nvidia-smi           # shows CUDA version in top right

# Common CUDA environment variables
[System.Environment]::SetEnvironmentVariable('CUDA_PATH',
    "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.3", 'Machine')

# Add CUDA bin and lib to PATH
$cudaPath = [System.Environment]::GetEnvironmentVariable('CUDA_PATH', 'Machine')
$currentPath = [System.Environment]::GetEnvironmentVariable('PATH', 'Machine')
if ($currentPath -notlike "*$cudaPath*") {
    [System.Environment]::SetEnvironmentVariable('PATH',
        "$currentPath;$cudaPath\bin;$cudaPath\libnvvp", 'Machine')
}

# cuDNN — copy files to CUDA directory after download
# cudnn64_*.dll → <CUDA_PATH>\bin
# cudnn.h       → <CUDA_PATH>\include
# cudnn.lib     → <CUDA_PATH>\lib\x64

# Verify device is visible to Python/PyTorch
# python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

## Multi-GPU / Hybrid graphics (laptops)

```powershell
# Check current GPU mode on hybrid (Optimus) systems
# MUX switch state — read from BIOS-exposed ACPI or OEM utility
# Most OEMs expose this via their own app (ASUS Armoury Crate, Lenovo Vantage, MSI Center)

# Force apps to use dGPU via registry (when no MUX switch)
# This is the "High performance GPU" setting from Windows Settings > Display > Graphics
$appPath = "C:\path\to\app.exe"
$regBase = 'HKCU:\SOFTWARE\Microsoft\DirectX\UserGpuPreferences'
New-Item -Path $regBase -Force | Out-Null
Set-ItemProperty -Path $regBase -Name $appPath -Value 'GpuPreference=2;'
# 0 = system default, 1 = power saving (iGPU), 2 = high performance (dGPU)

# Check which GPU is rendering a process
Get-Counter '\GPU Engine(*)\Utilization Percentage' |
    Select-Object -ExpandProperty CounterSamples |
    Where-Object CookedValue -gt 0 |
    Select-Object InstanceName, CookedValue |
    Sort-Object CookedValue -Descending

# nvidia-smi on laptop — shows display vs compute GPU separation
nvidia-smi -L   # list all GPUs
```

## Driver management

```powershell
# Get current driver version
(Get-WmiObject Win32_VideoController | Where-Object Name -match 'NVIDIA').DriverVersion

# Silent driver install (Game Ready or Studio driver)
# Download the .exe from nvidia.com, then:
.\555.85-desktop-win10-win11-64bit-international-dch-whql.exe -s -noreboot
# -s = silent, -noreboot = don't auto-reboot (you control timing)

# DDU (Display Driver Uninstaller) — clean removal before reinstall
# Download DDU from Wagnardsoft, then in Safe Mode:
& ".\DDU\Display Driver Uninstaller.exe" -silent -cleannvidia -removemono

# Check driver via Device Manager (get all display adapters)
Get-PnpDevice -Class Display | Select-Object FriendlyName, InstanceId, Status
```

## GPU process management

```powershell
# List processes using GPU and their VRAM
nvidia-smi --query-compute-apps=pid,used_memory,name --format=csv,noheader |
    ForEach-Object {
        $parts = $_ -split ','
        [PSCustomObject]@{
            PID     = $parts[0].Trim()
            VRAM_MB = $parts[1].Trim()
            Name    = $parts[2].Trim()
        }
    } | Sort-Object VRAM_MB -Descending

# Kill a process using GPU (e.g., runaway ML job)
$pid = (nvidia-smi --query-compute-apps=pid --format=csv,noheader |
    Select-Object -First 1).Trim()
Stop-Process -Id $pid -Force

# Monitor GPU processes in real-time
while ($true) {
    Clear-Host
    nvidia-smi pmon -s m -d 1 -c 1  # memory usage per process
    Start-Sleep -Seconds 3
}
```

## Fan and thermal management

```powershell
# Read temperature and fan speed
nvidia-smi --query-gpu=temperature.gpu,fan.speed --format=csv,noheader

# Fan curve control requires third-party tools — nvidia-smi only sets a fixed speed:
# nvidia-smi -i 0 --fan-control=1  # enable manual fan control (not all consumer GPUs)
# nvidia-smi -i 0 --fan-speed=75   # set to 75%

# For consumer GPUs use MSI Afterburner CLI (AfterburnerRemoteServerPlugin) or
# EVGA Precision X1 — these expose REST APIs or COM objects for scripted fan curves

# Temperature alert via monitoring loop
$threshold = 80  # Celsius
while ($true) {
    $temp = (nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits).Trim()
    if ([int]$temp -ge $threshold) {
        # Trigger notification
        Add-Type -AssemblyName System.Windows.Forms
        $balloon = New-Object System.Windows.Forms.NotifyIcon
        $balloon.Icon = [System.Drawing.SystemIcons]::Warning
        $balloon.Visible = $true
        $balloon.ShowBalloonTip(5000, "GPU Alert", "Temperature: ${temp}°C", [System.Windows.Forms.ToolTipIcon]::Warning)
        Write-Warning "GPU temperature ${temp}°C exceeded threshold ${threshold}°C at $(Get-Date)"
    }
    Start-Sleep -Seconds 30
}
```
