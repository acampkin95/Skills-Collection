# Privacy and Security Settings Guide

Configure macOS privacy and security settings.

## Security Preferences

### FileVault
```bash
# Check FileVault status
fdesetup status

# Enable FileVault (requires admin)
sudo fdesetup enable

# Add user to FileVault
sudo fdesetup add -usertoadd username
```

### Gatekeeper
```bash
# Check Gatekeeper status
spctl --status

# Assess an app
spctl --assess --type exec /Applications/AppName.app

# Allow app from unidentified developer
sudo spctl --add --label "Developer ID" /Applications/AppName.app
```

### System Integrity Protection (SIP)
```bash
# Check SIP status
csrutil status

# SIP must be disabled from Recovery Mode
# csrutil disable (in Recovery)
```

## Privacy Controls

### Location Services
```bash
# Check location services status
sudo launchctl list | grep -i location

# List apps with location access
sqlite3 ~/Library/Application\ Support/com.apple.locationd/LocationAgent \
       "SELECT bundleid FROM Clients"
```

### Camera and Microphone
```bash
# Check camera access
tccutil --list | grep Camera

# Check microphone access
tccutil --list | Microphone
```

### Full Disk Access
```bash
# Check Full Disk Access
tccutil --list | grep FullDiskAccess
```

## TCC Database Management

### Check TCC Permissions
```bash
# Read TCC database (requires Full Disk Access)
sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db \
       "SELECT client, auth_value, service FROM access WHERE client LIKE '%app%'"
```

### Reset TCC Permissions
```bash
# Delete TCC database (will reset all permissions)
rm ~/Library/Application\ Support/com.apple.TCC/TCC.db

# Or for specific app
tccutil reset Camera com.apple.FaceTime
```

## Firewall Configuration

### Enable/Disable Firewall
```bash
# Check status
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Enable
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on

# Disable
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
```

### Manage Application Rules
```bash
# Add app to firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw \
     --add /Applications/AppName.app

# Check app status
sudo /usr/libexec/ApplicationFirewall/socketfilterfw \
     --list /Applications/AppName.app
```

### Stealth Mode
```bash
# Enable stealth mode
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on

# Check status
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getstealthmode
```

## Network Security

### AirDrop
```bash
# Check AirDrop status
defaults read com.apple.airdrop

# Disable (requires Finder restart)
defaults write com.apple.airdrop ControllerDeterminedUSERSOnly -bool true
```

### Firewall Ports
```bash
# List allowed ports
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps

# Block incoming connections
sudo /usr/libexec/ApplicationFirewall/socketfilterfw \
     --setblockall on
```

## Password and Authentication

### Password Policy
```bash
# Check password policy
pwpolicy -getaccountpolicies

# Set minimum password length
pwpolicy -setpasswordpolicies -maxLifetime=365 \
         -minChars=12 -requiresAlpha=1 -requiresNumeric=1
```

### Touch ID
```bash
# Check Touch ID configuration
sudo defaults read /Library/Preferences/com.apple.touchid.plist

# Add fingerprint (System Preferences > Touch ID)
```

## Security Auditing

### Check for Weak Passwords
```bash
# Check user passwords
sudo pwpolicy -getaccountpolicies | grep -i "failed logins"
```

### View Security Logs
```bash
# View authentication logs
log show --predicate 'process == "sudo"' --info

# View firewall logs
log show --predicate 'process == "socketfilterfw"' --info
```

## App Sandboxing

### Check App Sandboxing
```bash
# Check if app is sandboxed
codesign -dvv /Applications/AppName.app 2>&1 | grep Sandbox
```

### Disable App Sandbox (Not Recommended)
- Only for development/testing
- Requires disabling SIP

## Security Recommendations

### Essential Settings

1. **Enable FileVault**
2. **Enable Firewall**
3. **Enable Automatic Updates**
4. **Use strong passwords**
5. **Enable Touch ID for sudo**

### Regular Maintenance

```bash
# Weekly security checks
#!/bin/bash
echo "=== Security Check ==="
echo "FileVault: $(fdesetup status | head -1)"
echo "Firewall: $(/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate)"
echo "SIP: $(csrutil status | grep -o 'enabled\|disabled')"
echo "Last login:"
last -1
```

### Monitoring Tools
```bash
# Activity Monitor for suspicious processes
open -a "Activity Monitor"

# Console app for log monitoring
open -a "Console"

# Keychain Access
open -a "Keychain Access"
```

## Privacy Tips

1. Review app permissions regularly
2. Disable Location Services for unused apps
3. Use private browsing in Safari
4. Review and clean up Keychain items
5. Check app accessibility permissions
