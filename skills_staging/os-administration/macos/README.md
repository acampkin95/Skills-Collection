# macOS Skill - Development and Administration

A comprehensive skill for macOS development, administration, and automation.

## Installation

No additional dependencies required. Uses system utilities:
- `brew` (Homebrew)
- `xcode-select` (Xcode CLI tools)
- `launchctl` (launchd management)
- `mdfind` (Spotlight)
- `osascript` (AppleScript)

## Usage

Import and use individual modules:

```python
from macos import brew_manager, xcode_helper, launchd_manager
from macos import spotlight_search, system_info, automation_helper

# Install Homebrew package
brew_manager.install("neovim")

# Manage launch agent
launchd_manager.load("/path/to/agent.plist")

# Search with Spotlight
results = spotlight_search.search("document")

# Get system information
info = system_info.get_system_info()

# Run AppleScript
automation_helper.run_applescript('tell app "Finder" to activate')
```

## Scripts Overview

### brew-manager.py
Homebrew package and formula management.

### xcode-helper.py
Xcode and iOS development environment setup.

### launchd-manager.py
LaunchAgent and LaunchDaemon configuration.

### spotlight-search.py
Spotlight search and metadata operations.

### system-info.py
System information gathering and diagnostics.

### automation-helper.py
AppleScript execution and automation.

## macOS Version Support

- macOS Ventura (13.x)
- macOS Sonoma (14.x)
- macOS Sequoia (15.x)

## Documentation

See reference docs:
- `brew-guide.md` - Homebrew best practices
- `launchd-reference.md` - launchd configuration
- `sequoia-features.md` - Sequoia new features
- `security-privacy.md` - Privacy settings
- `developer-tools.md` - Dev environment setup

## License

Part of Claude Code skills.
