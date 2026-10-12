# Windows 11 Administration Reference

## Service management

```powershell
# List all services with status
Get-Service | Sort-Object Status, DisplayName | Format-Table -AutoSize

# Start/stop/restart
Start-Service -Name wuauserv
Stop-Service -Name Spooler -Force
Restart-Service -Name W32Time

# Change startup type
Set-Service -Name Spooler -StartupType Disabled
Set-Service -Name wuauserv -StartupType Automatic

# Delayed auto-start (no direct PS cmdlet — use sc.exe)
sc.exe config wuauserv start= delayed-auto

# Configure recovery actions (restart on failure)
sc.exe failure Spooler reset= 86400 actions= restart/5000/restart/10000/restart/30000
# reset=seconds before reset, actions=action/delay_ms (up to 3 actions)

# Create a new service
New-Service -Name MyService -BinaryPathName "C:\MyApp\myapp.exe" `
    -DisplayName "My Application" -StartupType Automatic -Description "Does stuff"

# Query service with CIM (richer info than Get-Service)
Get-CimInstance -ClassName Win32_Service -Filter "Name='wuauserv'" |
    Select-Object Name, State, StartMode, PathName, StartName
```

## User and group management (local)

```powershell
# List local users
Get-LocalUser

# Create user
$password = ConvertTo-SecureString "P@ssword1!" -AsPlainText -Force
New-LocalUser -Name "jsmith" -Password $password -FullName "John Smith" `
    -Description "Developer account" -PasswordNeverExpires

# Add to group
Add-LocalGroupMember -Group "Administrators" -Member "jsmith"
Add-LocalGroupMember -Group "Remote Desktop Users" -Member "jsmith"

# Disable / remove
Disable-LocalUser -Name "jsmith"
Remove-LocalUser -Name "jsmith"

# List members of a group
Get-LocalGroupMember -Group "Administrators"
```

## Registry operations

### Key paths cheatsheet
| Purpose | Path |
|---------|------|
| Auto-run (user) | `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` |
| Auto-run (system) | `HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` |
| Installed apps (64-bit) | `HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall` |
| Installed apps (32-bit) | `HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall` |
| Environment (system) | `HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment` |
| Power settings | `HKLM:\SYSTEM\CurrentControlSet\Control\Power` |
| GPU TDR (timeout detection) | `HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers` |
| Explorer policies | `HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer` |
| Terminal/Console | `HKCU:\Console` |

### Types reference
| -Type value | Registry type |
|-------------|--------------|
| String | REG_SZ |
| ExpandString | REG_EXPAND_SZ |
| Binary | REG_BINARY |
| DWORD | REG_DWORD |
| MultiString | REG_MULTI_SZ |
| QWord | REG_QWORD |

```powershell
# Enumerate all values under a key
Get-ItemProperty -Path 'HKLM:\SOFTWARE\MyApp'

# Test if key exists
Test-Path -Path 'HKCU:\SOFTWARE\MyApp'

# Delete a value
Remove-ItemProperty -Path 'HKCU:\SOFTWARE\MyApp' -Name 'OldSetting'

# Delete entire key (recursive)
Remove-Item -Path 'HKCU:\SOFTWARE\MyApp' -Recurse

# Access remote registry (if RemoteRegistry service is running)
$reg = [Microsoft.Win32.RegistryKey]::OpenRemoteBaseKey('LocalMachine', 'server01')
$key = $reg.OpenSubKey('SOFTWARE\MyApp')
$key.GetValue('Setting')
```

## Event log querying

```powershell
# List all available logs
Get-WinEvent -ListLog * | Where-Object RecordCount -gt 0 | Sort-Object RecordCount -Descending

# Query by log name and time
Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    StartTime = (Get-Date).AddHours(-24)
    Level     = 2   # 1=Critical, 2=Error, 3=Warning, 4=Info, 5=Verbose
}

# Query by event ID
Get-WinEvent -FilterHashtable @{
    LogName = 'Application'
    Id      = 1000
}

# Query with XPath (most flexible)
Get-WinEvent -FilterXPath '*[System[EventID=4625]]' -LogName Security

# Common event IDs
# System:    6006=clean shutdown, 6008=dirty shutdown, 41=unexpected reboot
# Security:  4624=logon success, 4625=logon failure, 4648=explicit creds logon
# Graphics:  4101=TDR recovery (GPU hang), 4117=TDR error

# Export to CSV
Get-WinEvent -FilterHashtable @{ LogName='Application'; Level=2 } |
    Select-Object TimeCreated, Id, Message |
    Export-Csv -Path .\errors.csv -NoTypeInformation
```

## Scheduled tasks

```powershell
# Create a task that runs a PS script on logon
$action = New-ScheduledTaskAction -Execute 'pwsh.exe' `
    -Argument '-NonInteractive -WindowStyle Hidden -File "C:\Scripts\startup.ps1"'
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -RunOnlyIfNetworkAvailable:$false
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest

Register-ScheduledTask -TaskName 'MyStartupScript' -Action $action `
    -Trigger $trigger -Settings $settings -Principal $principal

# Run on schedule (daily at 2am)
$trigger = New-ScheduledTaskTrigger -Daily -At '02:00'
Register-ScheduledTask -TaskName 'NightlyCleanup' -Action $action -Trigger $trigger `
    -RunLevel Highest

# List tasks
Get-ScheduledTask | Where-Object State -ne 'Disabled' | Format-Table TaskName, State

# Run immediately
Start-ScheduledTask -TaskName 'MyStartupScript'

# Remove
Unregister-ScheduledTask -TaskName 'MyStartupScript' -Confirm:$false
```

## Windows Firewall

```powershell
# Allow an app through firewall
New-NetFirewallRule -DisplayName 'MyApp' -Direction Inbound `
    -Program 'C:\MyApp\myapp.exe' -Action Allow -Profile Domain,Private

# Allow a port
New-NetFirewallRule -DisplayName 'Allow 8080 TCP' -Direction Inbound `
    -LocalPort 8080 -Protocol TCP -Action Allow

# Block outbound for specific app
New-NetFirewallRule -DisplayName 'Block MyApp Outbound' -Direction Outbound `
    -Program 'C:\MyApp\myapp.exe' -Action Block

# List rules
Get-NetFirewallRule | Where-Object Enabled -eq $true |
    Get-NetFirewallPortFilter | Select-Object * | Format-Table

# Remove a rule
Remove-NetFirewallRule -DisplayName 'MyApp'

# Enable/disable firewall profile
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

## WMI / CIM reference

Always prefer `Get-CimInstance` over `Get-WmiObject` (deprecated in PS7).

| What you need | CIM class |
|---------------|-----------|
| CPU info | `Win32_Processor` |
| RAM | `Win32_PhysicalMemory` |
| Disk | `Win32_DiskDrive`, `Win32_LogicalDisk` |
| GPU | `Win32_VideoController` |
| OS info | `Win32_OperatingSystem` |
| Running processes | `Win32_Process` |
| Services | `Win32_Service` |
| Network adapters | `Win32_NetworkAdapterConfiguration` |
| BIOS | `Win32_BIOS` |
| Motherboard | `Win32_BaseBoard` |
| Battery | `Win32_Battery` |
| Installed software | `Win32_Product` *(slow — avoid; use Uninstall registry key instead)* |

```powershell
# System summary
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber, TotalVisibleMemorySize

# Disk space
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" |
    Select-Object DeviceID,
        @{N='Size(GB)';E={[math]::Round($_.Size/1GB,1)}},
        @{N='Free(GB)';E={[math]::Round($_.FreeSpace/1GB,1)}},
        @{N='Free%';E={[math]::Round($_.FreeSpace/$_.Size*100,1)}}

# GPU info
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, VideoMemoryType, AdapterRAM
```

## Group Policy (local)

```powershell
# Apply/update Group Policy
gpupdate /force

# Generate HTML report
gpresult /H C:\gpreport.html /F

# Use LGPO.exe (Microsoft tool) for scripted local policy
# Download: https://www.microsoft.com/en-us/download/details.aspx?id=55319
# Apply a policy backup
lgpo.exe /g "C:\PolicyBackup"

# secedit — security policy settings
secedit /export /cfg C:\secpolicy.inf
secedit /configure /db C:\secpolicy.sdb /cfg C:\secpolicy.inf /overwrite
```

## Windows Update automation

```powershell
# Install PSWindowsUpdate module (one-time)
Install-Module -Name PSWindowsUpdate -Force -Scope CurrentUser

# Check for updates
Get-WindowsUpdate

# Install all updates
Install-WindowsUpdate -AcceptAll -AutoReboot

# Install specific KB
Install-WindowsUpdate -KBArticleID KB5012345 -AcceptAll

# Hide an update
Hide-WindowsUpdate -KBArticleID KB5012345

# Via WUA COM object (no module needed, works in constrained environments)
$UpdateSession = New-Object -ComObject Microsoft.Update.Session
$UpdateSearcher = $UpdateSession.CreateUpdateSearcher()
$SearchResult = $UpdateSearcher.Search("IsInstalled=0")
$SearchResult.Updates | Select-Object Title, IsDownloaded
```

## WinGet scripting

```powershell
# Install a package
winget install --id Microsoft.VisualStudioCode --silent --accept-package-agreements --accept-source-agreements

# Upgrade all
winget upgrade --all --silent --accept-package-agreements

# Export installed packages
winget export -o C:\winget-packages.json

# Import / restore packages
winget import -i C:\winget-packages.json --accept-package-agreements

# Search
winget search "visual studio"

# Scripted bulk install from array
$packages = @(
    'Git.Git',
    'Microsoft.VisualStudioCode',
    'GitHub.GitHubDesktop',
    'Postman.Postman'
)
foreach ($pkg in $packages) {
    Write-Host "Installing $pkg..."
    winget install --id $pkg --silent --accept-package-agreements --accept-source-agreements
}
```

## Performance & diagnostics

```powershell
# CPU, memory, disk snapshot
Get-Counter '\Processor(_Total)\% Processor Time',
             '\Memory\Available MBytes',
             '\PhysicalDisk(_Total)\Disk Bytes/sec' -SampleInterval 2 -MaxSamples 5

# Top CPU processes
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, Id, CPU, WorkingSet

# Network connections
Get-NetTCPConnection -State Established | Sort-Object LocalPort |
    Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, OwningProcess

# Startup programs (beyond scheduled tasks)
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User
```
