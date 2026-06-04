# Serial-over-LAN (SoL) Setup Guide

SoL provides text-based remote console access via IPMI's serial redirection. Unlike KVM (which mirrors the video output), SoL sends serial console output over the network. This is lighter-weight and works when KVM is unavailable, but requires the OS to output to a serial port.

## Why SoL Shows No Output

By default, most Linux installations only output to the VGA console (`tty0`). The IPMI serial port (`ttyS0` or `ttyS1`) receives nothing unless explicitly configured. A blank SoL screen doesn't mean the server is down — it means serial console output isn't configured.

## Configuring GRUB for SoL

### Step 1: Identify the Serial Port

Most OVH servers use `ttyS0` (COM1) at unit 0. Some newer boards use `ttyS1`.

To check (if you have SSH access):
```bash
dmesg | grep -i serial
# or
cat /proc/tty/driver/serial
```

### Step 2: Edit GRUB Configuration

```bash
sudo nano /etc/default/grub
```

Add or modify these lines:

```bash
# Send console output to both VGA and serial
GRUB_CMDLINE_LINUX_DEFAULT="nomodeset console=tty0 console=ttyS0,115200n8"

# GRUB menu accessible from both VGA and serial
GRUB_TERMINAL="console serial"

# Serial port parameters matching IPMI BMC settings
GRUB_SERIAL_COMMAND="serial --unit=0 --speed=115200 --word=8 --parity=no --stop=1"
```

**Parameters explained**:
- `nomodeset` — Disables kernel mode-setting (prevents graphics driver from taking over console)
- `console=tty0` — Keep VGA console active (for KVM)
- `console=ttyS0,115200n8` — Add serial console: port ttyS0, 115200 baud, 8N1
- `--unit=0` — Serial port unit (0 = ttyS0/COM1, 1 = ttyS1/COM2)
- `--speed=115200` — Baud rate (must match IPMI BMC settings)

### Step 3: Update GRUB

```bash
sudo update-grub
```

### Step 4: Reboot and Test

```bash
sudo reboot
```

Then access SoL via:
```bash
python3 scripts/ovh_server.py ipmi SERVER_NAME --sol-web
# or
python3 scripts/ovh_server.py ipmi SERVER_NAME --sol-ssh
```

## Enabling getty on Serial Port

To get a login prompt on the serial console (not just boot messages):

### systemd (Debian 8+, Ubuntu 16.04+, CentOS 7+)

```bash
sudo systemctl enable serial-getty@ttyS0.service
sudo systemctl start serial-getty@ttyS0.service
```

### Manual (older systems)

Add to `/etc/inittab`:
```
S0:2345:respawn:/sbin/agetty -L ttyS0 115200 vt100
```

Then: `sudo telinit q`

## Common Issues

### SoL shows garbage characters
- Baud rate mismatch between GRUB config and IPMI BMC
- Try 9600 instead of 115200: change both GRUB and test again

### SoL shows GRUB menu but no OS output
- Missing `console=ttyS0,115200n8` in `GRUB_CMDLINE_LINUX_DEFAULT`
- The `console=` parameter must be on the kernel command line, not just GRUB

### SoL shows login prompt but keyboard doesn't work
- Known Firefox bug with Shell-in-a-box: minus/dash key doesn't register
- Workaround: use numpad minus, or switch to Chrome
- Alternative: use `--sol-ssh` instead of `--sol-web`

### Wrong serial port (ttyS0 vs ttyS1)
- Try unit=1 and ttyS1 if unit=0/ttyS0 shows nothing
- Check IPMI BMC docs for your specific motherboard

## Rescue Mode SoL

OVH rescue mode typically has serial console pre-configured. If not:
1. Boot into rescue via `ovh_server.py rescue SERVER --enable && ovh_server.py reboot SERVER`
2. Access via SoL — rescue netboot images usually output to serial
3. If still blank, use KVM instead (`--kvm-html`)
