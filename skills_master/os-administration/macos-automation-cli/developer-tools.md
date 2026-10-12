# macOS Development Environment Guide

Set up and configure a macOS development environment.

## Command Line Tools

### Install Xcode CLI Tools
```bash
# Interactive install
xcode-select --install

# Non-interactive (downloads DMG)
sudo installer -pkg /Library/Developer/CommandLineTools/\
    Packages/macOS_SDK_headers_for_macOS_*.pkg -target /
```

### Verify Installation
```bash
# Check CLI tools path
xcode-select -p

# Check versions
clang --version
swift --version
git --version
```

## Homebrew Setup

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add to PATH (Intel)
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile

# Add to PATH (Apple Silicon)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile

eval "$(/opt/homebrew/bin/brew shellenv)"
```

## Git Configuration

```bash
# Configure identity
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# Configure editor
git config --global core.editor nvim

# Configure aliases
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch

# Enable colored output
git config --global color.ui auto

# Set default branch
git config --global init.defaultBranch main
```

## Python Environment

### Using pyenv
```bash
# Install pyenv
brew install pyenv

# Add to shell
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# Install Python versions
pyenv install 3.12.0
pyenv install 3.11.5

# Set global version
pyenv global 3.12.0
```

### Using virtualenv
```bash
# Create virtual environment
python -m venv myproject_env

# Activate
source myproject_env/bin/activate

# Deactivate
deactivate
```

## Node.js Environment

### Using nvm
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Load nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Install Node.js versions
nvm install 20
nvm install 18

# Set default
nvm alias default 20
```

### Using fnm (faster alternative)
```bash
brew install fnm

# Add to shell
echo 'eval "$(fnm env --shell-on-install)"' >> ~/.zshrc

# Install and use version
fnm install 20
fnm use 20
```

## Rust Installation

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Add to PATH
source "$HOME/.cargo/env"

# Install additional tools
cargo install ripgrep fd bat exa
```

## Go Installation

```bash
# Install via Homebrew
brew install go

# Verify
go version

# Set GOPATH
export GOPATH="$HOME/go"
export PATH="$PATH:$GOPATH/bin"
```

## Ruby Environment

### Using rbenv
```bash
# Install rbenv
brew install rbenv ruby-build

# Add to shell
echo 'eval "$(rbenv init -)"' >> ~/.zshrc

# Install Ruby version
rbenv install 3.2.2
rbenv global 3.2.2

# Rehash
rbenv rehash
```

## Docker Setup

```bash
# Install Docker Desktop
brew install --cask docker

# Start Docker Desktop
open -a Docker

# Verify
docker run hello-world
```

## Database Tools

```bash
# PostgreSQL
brew install postgresql
brew services start postgresql

# MySQL
brew install mysql
brew services start mysql

# Redis
brew install redis
brew services start redis

# MongoDB
brew install mongodb-community
brew services start mongodb-community
```

## Text Editors and IDEs

### Neovim
```bash
brew install nvim

# Configuration directory
mkdir -p ~/.config/nvim
```

### VS Code
```bash
brew install --cask visual-studio-code

# CLI integration
code --install-extension ms-python.python
```

### JetBrains Tools
```bash
# IntelliJ IDEA
brew install --cask intellij-idea

# PyCharm
brew install --cask pycharm
```

## Shell Configuration

### Oh My Zsh
```bash
# Install Oh My Zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Useful plugins
plugins=(
    git
    docker
    python
    node
    npm
    rbenv
    pyenv
    vscode
)
```

### Aliases
```bash
# Add to ~/.zshrc
alias ll='ls -la'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline'
alias dcu='docker-compose up'
alias dcd='docker-compose down'
```

## Environment Variables

### Common Variables
```bash
# Add to ~/.zshrc
export EDITOR='nvim'
export VISUAL='nvim'

# Language-specific
export PYENV_ROOT="$HOME/.pyenv"
export NVM_DIR="$HOME/.nvm"
export PATH="$PATH:$HOME/.local/bin"
```

## SDK Management

### Android SDK
```bash
# Install via Homebrew
brew install --cask android-sdk

# Add to PATH
export ANDROID_SDK_ROOT="/usr/local/share/android-sdk"
export PATH="$PATH:$ANDROID_SDK_ROOT/tools:$ANDROID_SDK_ROOT/platform-tools"
```

### AWS CLI
```bash
# Install AWS CLI v2
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Verify
aws --version
```

## Troubleshooting

### Permission Issues
```bash
# Fix Homebrew permissions
sudo chown -R $(whoami) /opt/homebrew

# Fix npm global permissions
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH=~/.npm-global/bin:$PATH
```

### Path Issues
```bash
# Check PATH
echo $PATH

# Add to path
export PATH="/new/path:$PATH"

# Verify command locations
which python
which node
which git
```

### Clean Reinstall
```bash
# Uninstall Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/uninstall.sh)"

# Reinstall Node.js/npm packages
rm -rf node_modules package-lock.json
npm install

# Reinstall Python packages
pip freeze > requirements.txt
pip install -r requirements.txt
```

## Development Tools Summary

| Tool | Purpose | Install Command |
|------|---------|-----------------|
| Homebrew | Package manager | See above |
| Git | Version control | Pre-installed |
| Python | Python runtime | pyenv |
| Node.js | JavaScript runtime | nvm/fnm |
| Rust | Rust toolchain | rustup |
| Go | Go runtime | Homebrew |
| Docker | Containers | Homebrew Cask |
| PostgreSQL | Database | Homebrew |
| Redis | Cache/Queue | Homebrew |
| Neovim | Text editor | Homebrew |
| VS Code | IDE | Homebrew Cask |
