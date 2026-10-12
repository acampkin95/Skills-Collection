# Homebrew Best Practices

Guide for using Homebrew effectively on macOS.

## Installation

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add to PATH (Apple Silicon)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

## Package Management

### Installing Packages
```bash
# Install a formula
brew install neovim

# Install specific version
brew install postgresql@15

# Install from head (unstable)
brew install --HEAD neovim

# Install with options
brew install mysql --with-debug --with-innodb
```

### Managing Casks
```bash
# Install GUI application
brew install --cask visual-studio-code

# Install from specific tap
brew install --cask homebrew/cask-fonts/font-hack-nerd-font

# Force install (skip verification)
brew install --cask --force firefox
```

### Upgrading
```bash
# Upgrade all
brew upgrade

# Upgrade specific package
brew upgrade neovim

# Upgrade Homebrew itself
brew update && brew upgrade brew
```

### Cleanup
```bash
# Remove old versions
brew cleanup

# Dry run first
brew cleanup --dry-run

# Remove unused dependencies
brew autoremove
```

## Dependency Management

### Checking Dependencies
```bash
# Show dependencies
brew deps neovim

# Show reverse dependencies
brew uses neovim --installed

# Check for broken dependencies
brew doctor
```

### Pinning Versions
```bash
# Pin a formula to current version
brew pin postgresql@15

# List pinned
brew list --pinned

# Unpin
brew unpin postgresql@15
```

## Tap Management

### Official Taps
```bash
# Core formulas
brew tap homebrew/core

# Casks
brew tap homebrew/cask

# Services
brew tap homebrew/services

# Font packages
brew tap homebrew/cask-fonts
```

### Third-Party Taps
```bash
# Add a tap
brew tap user/repo

# Remove a tap
brew untap user/repo

# List all taps
brew tap
```

## Troubleshooting

### Common Issues

**Permission denied:**
```bash
# Fix permissions
sudo chown -R $(whoami) /opt/homebrew/bin/brew
```

**Cask verification failed:**
```bash
# Re-download
brew reinstall --cask visual-studio-code

# Skip verification
brew install --cask --no-quarantine firefox
```

**Dependency conflicts:**
```bash
# Check what's using a dependency
brew uses --installed openssl@3

# Force link
brew link --force openssl@3
```

### Resetting Homebrew
```bash
# Reinstall Homebrew
/bin/bash - "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## Performance Tips

### Parallel Installs
```bash
# Use all CPU cores (built-in to brew)
brew install -j $(nproc) neovim
```

### Skip Unnecessary Steps
```bash
# Skip post-install audit
brew install --no-audit neovim

# Skip cleanup
brew install --no-cleanup neovim
```

## Common Commands Reference

| Command | Description |
|---------|-------------|
| `brew search <query>` | Search for packages |
| `brew info <package>` | Show package info |
| `brew list` | List installed packages |
| `brew outdated` | Check for updates |
| `brew switch <package> <version>` | Switch versions |
| `brew link --overwrite <package>` | Fix linking issues |
| `brew uninstall <package>` | Remove package |
| `brew leaves` | List installed without dependencies |
