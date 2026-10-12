# macOS Sequoia Features

Guide to new features and capabilities in macOS Sequoia (15.x).

## Apple Intelligence

### System-Wide AI Features
```bash
# Check if Apple Intelligence is available
system_profiler SPSoftwareDataType | grep "Apple Intelligence"
```

### Writing Tools
- Built-in AI writing assistance across apps
- Rewrite, summarize, and proofread features
- Available in Mail, Notes, Pages, and Safari

### Image Playground
- Generate images from descriptions
- Access via Photos app or standalone app
- Privacy-focused: runs on-device

### Siri Enhancements
- Better context awareness
- On-screen awareness
- Improved natural language understanding

## iPhone Mirroring

### Overview
Control your iPhone from your Mac.

```bash
# Launch iPhone Mirroring
open -a "iPhone Mirroring"
```

### Requirements
- macOS Sequoia
- iPhone running iOS 18
- Same Apple ID signed in
- Bluetooth and Wi-Fi enabled

## Enhanced Window Tiling

### New Features
- Better window snapping
- More tile configurations
- Keyboard shortcuts for positioning

### Shortcuts
```
Control + Left Arrow    -> Tile to left
Control + Right Arrow   -> Tile to right
Control + Up Arrow      -> Maximize
```

## Passwords App

### New Standalone App
```bash
# Open Passwords app
open -a "Passwords"
```

### Features
- Syncs with iCloud Keychain
- Categories (Passkeys, Wi-Fi, Security Codes)
- Built-in authentication
- Windows compatibility via iCloud

## Safari Updates

### Highlights
- Web items in Reading List
- Improved Reader mode
- Distraction control
- Enhanced隐私 reports

### Native Password Import
```bash
# Import from other browsers
# Safari > Settings > Passwords > Import
```

## Privacy and Security

### Enhanced Privacy Controls
- More granular app permission controls
- Improved location privacy
- FaceTime end-to-end encryption

### Security Features
- Passkeys support across apps
- Enhanced malware protection
- Lockdown Mode improvements

## Gaming Features

### Game Mode Enhancements
- Automatic Game Mode for all games
- Improved AirPods latency
- Better CPU/GPU allocation

### Game Porting Toolkit 2
```bash
# Check version
gtkd --version
```

## Developer Features

### Xcode 16 Integration
- Build time improvements
- Enhanced Swift testing
- Previews with Apple Intelligence

### New System APIs
- Writing Tools integration
- Image Playground API
- Enhanced MapKit

## System Enhancements

### Calculator App
- Scientific calculator
- Math notes in Notes app
- Unit conversions

### Notes App
- Math expressions in notes
- Voice notes
- Improved collaboration

### Calendar
- Improved event creation
- Holiday calendars
- Reminders integration

## Setup and Migration

### Clean Install
```bash
# Create macOS Sequoia installer
# Download from Mac App Store
# Create bootable USB
```

### Check Version
```bash
sw_vers -productVersion
# Should return 15.x
```

## Compatibility

### Supported Macs
- MacBook Pro (2021+)
- MacBook Air (2022+)
- iMac (2021+)
- Mac mini (2023+)
- Mac Studio (2022+)
- Mac Pro (2023+)

### Rosetta Requirements
- Most Intel apps still work
- Some apps may need Rosetta
- Check app compatibility before upgrading

## New Terminal Commands

### systemsetup (Deprecated)
Many legacy systemsetup commands now require sudo or are replaced:

```bash
# Instead of:
systemsetup -settimezone "America/Los_Angeles"

# Use:
sudo tzutil -s "America/Los_Angeles"
```

## Tips and Tricks

### Quick Actions
1. Control-click for context menus
2. Use Stage Manager for organization
3. Enable Focus modes

### Performance
- Use Activity Monitor to check Apple Intelligence usage
- Monitor memory pressure with `vm_stat`
- Check energy impact with `pmset -g`
