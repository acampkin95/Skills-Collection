---
name: macos
description: "Use this skill when working with macOS, macos automation, AppleScript, Homebrew, Mac shortcuts."
---

# macOS Automation & Development (Sequoia/Sonoma)

Expert in macOS Sequoia (15.x) and Sonoma (14.x) automation, development tools (Xcode, Swift), system administration, and productivity workflows.

## Capabilities

- Homebrew package management and optimization
- Xcode and iOS development environment management
- LaunchAgent/LaunchDaemon configuration and management
- Spotlight search and metadata operations
- System information gathering and diagnostics
- AppleScript and automation scripting
- Privacy and security configuration
- macOS Sequoia/Sonoma feature utilization
- Swift package development
- System networking and connectivity

## macOS 2026 Development Features

### Sequoia (15.x) & Sonoma (14.x) Highlights

**Performance & Optimization**
- Responsive Scrolling: GPU-accelerated scrolling for all applications
- Gaming Mode: Improved frame pacing and reduced latency for games
- App Nap improvements: Better idle detection reduces unnecessary CPU usage
- Reduced Motion API: Smoother animations for accessibility-conscious apps

**Developer Tools**
- Xcode 16.1+: Enhanced Swift Package Manager with local dependency resolution
- Swift 6: Strict concurrency checking by default, improved async/await performance
- Metal 3.2: Ray tracing improvements, dynamic resolution scaling for games
- CoreML 8: On-device LLM inference with privacy guarantees (no cloud transmission)

**Privacy & Security (2026 Focus)**
- App Privacy Report: Granular per-app tracking transparency
- Locked folders: iCloud Drive encrypted folder support
- Mail tracking prevention: Automatic prevention of tracking pixels
- Safari private browsing improvements: Enhanced fingerprinting protection
- Microphone/Camera indicators: Persistent visual feedback when accessed

**System Architecture**
- Apple Silicon (M4/M4 Pro/M4 Max): 40% faster CPU, 50% better GPU performance
- Unified Memory: Shared memory pools reduce data copying (8GB-96GB variants)
- Rosetta 2 v2: Near-native performance for Intel binaries

### Automation & Workflow Tools

**Shortcuts App (2026 Updates)**
- Native CoreML support for on-device ML inference
- Improved file handling with iCloud Drive
- New Ask for Number/Text with validation
- Folder actions trigger support

**System Events & Automation**
- Login items management via command line (new in Sonoma+)
- Focusable window groups for organization
- Background app refresh notifications

## Usage

Use this skill when you need to:

- Manage Homebrew packages and dependencies
- Configure system services with launchd
- Automate macOS-specific tasks with AppleScript
- Gather system information and diagnostics
- Work with Xcode command line tools
- Configure privacy and security settings
- Use Spotlight for file search and metadata
- Develop Swift packages and apps
- Optimize system performance
- Debug system-level issues

## Common Tasks

### Homebrew Management

```bash
# Install a package
brew install node

# Update all packages
brew upgrade

# Search for packages
brew search database

# List installed packages
brew list

# Remove unused dependencies
brew autoremove
```

### LaunchAgent Configuration

```bash
# Create a plist at ~/Library/LaunchAgents/com.example.myscript.plist
# Run it with launchctl
launchctl load ~/Library/LaunchAgents/com.example.myscript.plist

# Unload a service
launchctl unload ~/Library/LaunchAgents/com.example.myscript.plist

# Check if running
launchctl list | grep com.example
```

### System Information

```bash
# Hardware info
system_profiler SPHardwareDataType

# Get OS version
sw_vers

# Check CPU architecture
uname -m   # arm64 or x86_64

# Memory usage
vm_stat
```

### AppleScript Automation

```applescript
-- Launch an app
tell application "Finder"
  activate
end tell

-- Run shell command
do shell script "brew update"

-- Create folder
tell application "Finder"
  make new folder at desktop with properties {name:"MyFolder"}
end tell
```

### Swift Package Development

```bash
# Create a new package
swift package init --type executable --name myapp

# Build and test
swift build
swift test

# Add dependency to Package.swift
swift package add https://github.com/user/package.git
```

## Scripts

| Script | Purpose |
|--------|---------|
| `brew-manager.py` | Homebrew package management and optimization |
| `xcode-helper.py` | Xcode and iOS development tools |
| `launchd-manager.py` | LaunchAgent/LaunchDaemon management |
| `spotlight-search.py` | Spotlight and file search operations |
| `system-info.py` | System information and diagnostics |
| `automation-helper.py` | AppleScript and automation helpers |

## Reference Docs

- `brew-guide.md` - Homebrew best practices and recipes
- `launchd-reference.md` - LaunchAgent configuration patterns
- `sequoia-features.md` - macOS Sequoia 15.x features and APIs
- `sonoma-features.md` - macOS Sonoma 14.x features and APIs
- `security-privacy.md` - Privacy and security configuration
- `developer-tools.md` - Xcode, Swift, and development environment
- `apple-silicon.md` - Apple Silicon optimization and Rosetta 2

## Quick Reference

### Essential Directories

```
~/Library/LaunchAgents/       # User-level services
/Library/LaunchDaemons/       # System-level services
~/Library/Application Support/# App config and data
~/Library/Preferences/        # User preferences
/usr/local/bin/              # Homebrew binary location (Intel)
/opt/homebrew/bin/           # Homebrew binary location (Apple Silicon)
```

### Permission Management

```bash
# Add execute permission
chmod +x /path/to/script

# Change file owner
chown user:group /path/to/file

# Get file permissions
ls -l /path/to/file

# Get folder permissions recursively
chmod -R 755 /path/to/folder
```

### Network Diagnostics

```bash
# Check connectivity
ping google.com

# DNS resolution
nslookup example.com
dig example.com

# Network interface info
ifconfig

# Route table
netstat -r
```

## Pro Tips

1. **Use Homebrew's bundle file** to manage multiple packages: `brew bundle --file=Brewfile`
2. **LaunchAgent timing** - use `StartInterval` for periodic tasks, `WatchPaths` for file monitoring
3. **System Preferences** - Use `defaults` command for scriptable preference management
4. **Spotlight indexing** - Exclude development folders to improve performance: `System Preferences > Siri & Spotlight > Exclude`
5. **Rosetta 2** - Check architecture compatibility before installing M1/M2 packages
6. **Security scanning** - Use `spctl` to verify app signatures and gatekeeper status
7. **Console.app** - Monitor system logs for troubleshooting (not just Terminal errors)

## Debugging macOS Issues

### App Won't Launch
1. Check gatekeeper: `spctl -a -vvv -t open --ignore-cache /path/to/app`
2. Verify code signature: `codesign -vvv /path/to/app`
3. Check Console.app logs for crash reports
4. Reset Launch Services: `defaults write com.apple.LaunchServices/com.apple.launchservices.secure.plist RestoreLog -bool YES`

### Performance Issues
1. Activity Monitor: Find CPU/memory hogs
2. Check for misbehaving LaunchAgents: `launchctl list | grep -i agent`
3. Disable Spotlight indexing: `mdutil -i off /`
4. Restart Finder: `killall Finder`

### Network Problems
1. Flush DNS cache: `dscacheutil -flushcache`
2. Check routing: `netstat -rn`
3. Reset network settings: System Preferences > Network > Advanced
4. Monitor network traffic: `nettop` in Terminal

## Integration with Development Workflows

This skill integrates with:
- **git-advanced-workflows** - macOS-specific git hooks via LaunchAgents
- **nextjs** - Xcode integration for iOS companion apps
- **docker-compose** - Homebrew Docker installation and management
- **environment-secrets** - .env file management via LaunchAgents
- **github-actions-ci** - macOS-specific CI runners and optimization
