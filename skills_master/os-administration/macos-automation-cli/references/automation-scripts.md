# macOS Automation Scripts: AppleScript, Shell, and Shortcuts Patterns

Reference guide for common macOS automation patterns using AppleScript, shell scripting, and Shortcuts.

## AppleScript Patterns

### Basic Application Control

Launch and control applications:

```applescript
-- Launch an application
tell application "Finder"
  activate
end tell

-- Check if application is running
tell application "System Events"
  if (application processes where name is "Safari") exists then
    display alert "Safari is running"
  end if
end tell

-- Quit application
tell application "Xcode"
  quit
end tell

-- Delay before action
delay 2  -- 2 seconds
```

### File and Folder Operations

```applescript
-- Create folder
tell application "Finder"
  make new folder at desktop with properties {name:"My Folder"}
end tell

-- Copy file
tell application "Finder"
  duplicate file "Macintosh HD:Users:you:Documents:file.txt" ¬
    to folder "Macintosh HD:Users:you:Desktop:"
end tell

-- Move file
tell application "Finder"
  move file "file.txt" of desktop to folder "Documents"
end tell

-- Empty trash
tell application "Finder"
  empty the trash
end tell

-- Get folder contents
tell application "Finder"
  set file_list to name of every file in the home folder
end tell
```

### Shell Command Execution

```applescript
-- Execute shell command
do shell script "brew update"

-- With output capture
set result to do shell script "ls -la /Users"

-- With elevated privileges
do shell script "sudo killall Dock" with administrator privileges

-- With password (not recommended)
do shell script "npm install" with administrator privileges ¬
  password "password123"
```

### Notification and Dialogs

```applescript
-- Simple notification
display notification "Task complete" with title "Build"

-- Alert dialog
display alert "File not found" message "The file could not be found at the specified path." ¬
  buttons {"OK", "Cancel"} default button 1

-- Input dialog
set user_input to display dialog "Enter your name:" default answer ""
set name to text returned of user_input

-- Choose from list
set selected to choose from list {"Option A", "Option B", "Option C"} ¬
  with title "Pick one" with prompt "Choose an option"
```

### Mail Operations

```applescript
-- Send email
tell application "Mail"
  set new_message to make new outgoing message with properties ¬
    {subject:"Hello", content:"Message body"}
  tell new_message
    make new to recipient at end of to recipients ¬
      with properties {address:"recipient@example.com"}
    send
  end tell
end tell

-- Get unread mail count
tell application "Mail"
  set unread_count to unread count of inbox
  display notification unread_count as text
end tell
```

### Calendar and Reminders

```applescript
-- Create calendar event
tell application "Calendar"
  set new_event to make new event at the end of events ¬
    with properties {title:"Meeting", start date:(current date), ¬
    end date:(current date) + 3600}
end tell

-- Create reminder
tell application "Reminders"
  set new_reminder to make new reminder in the default list ¬
    with properties {name:"Task", due date:date "2026-03-01"}
end tell
```

### System Information

```applescript
-- Get macOS version
set macos_version to system version of (system info)

-- Get current user
set current_user to do shell script "whoami"

-- Check disk space
set disk_info to do shell script "df -h / | tail -1"

-- Get uptime
set uptime to do shell script "uptime"
```

## Shell (zsh) Scripts

### Homebrew Package Management

```bash
#!/bin/zsh

# Update all packages
brew update
brew upgrade

# Install package
brew install node
brew install --cask visual-studio-code

# List installed packages
brew list

# Search for packages
brew search python

# Remove package
brew uninstall node
brew autoremove  # Remove unused dependencies

# Show package info
brew info node

# Check for outdated packages
brew outdated

# Pin package (prevent updates)
brew pin node

# Unpin package
brew unpin node

# Cleanup cache
brew cleanup
```

### File and Directory Operations

```bash
#!/bin/zsh

# Create backup
backup_dir="$HOME/Backups/$(date +%Y%m%d)"
mkdir -p "$backup_dir"
cp -r "$HOME/Documents" "$backup_dir/"

# Find files by date
find "$HOME/Downloads" -mtime +7 -delete  # Delete files older than 7 days

# Search in files
grep -r "search_term" "$HOME/Documents" --include="*.txt"

# Rename multiple files
cd "$HOME/Documents"
for file in *.jpg; do
  mv "$file" "${file%.jpg}.png"
done

# Compress directory
tar -czf archive.tar.gz documents/

# Extract archive
tar -xzf archive.tar.gz
```

### System Monitoring

```bash
#!/bin/zsh

# CPU and memory usage
top -l 1 | head -n 10

# Disk usage
df -h

# Network info
ifconfig | grep "inet " | head -n 1

# Active ports
lsof -i -P -n

# Running processes
ps aux | grep node

# System uptime
uptime

# Last login
last -n 1

# Battery status
pmset -g batt
```

### LaunchAgent Management

```bash
#!/bin/zsh

# Load LaunchAgent
launchctl load ~/Library/LaunchAgents/com.example.myscript.plist

# Unload LaunchAgent
launchctl unload ~/Library/LaunchAgents/com.example.myscript.plist

# List all agents
launchctl list | grep com.example

# Check if running
launchctl list | grep -q "com.example.myscript" && echo "Running" || echo "Not running"

# View agent logs
log stream --predicate 'eventMessage contains "com.example"'

# Enable agent at startup
launchctl enable gui/$(id -u)/com.example.myscript
```

### Development Environment Setup

```bash
#!/bin/zsh

# Install Xcode command line tools
xcode-select --install

# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Setup Ruby (for development)
brew install rbenv
rbenv install 3.2.0
rbenv global 3.2.0

# Setup Node.js
brew install nvm
nvm install 20
nvm use 20

# Setup Python
brew install python
pip3 install --upgrade pip

# Install common dev tools
brew install git curl wget git-lfs

# Setup git
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### Automated Backups

```bash
#!/bin/zsh

backup_source="$HOME/Documents"
backup_dest="/Volumes/ExternalDrive/Backups"
backup_date=$(date +%Y%m%d_%H%M%S)

# Check if drive is mounted
if [ ! -d "$backup_dest" ]; then
  echo "Backup drive not found"
  exit 1
fi

# Create backup
rsync -avz --delete "$backup_source/" "$backup_dest/Documents_$backup_date/"

# Log backup
echo "Backup completed: $backup_date" >> "$HOME/.backup.log"

# Cleanup old backups (keep last 7)
find "$backup_dest" -maxdepth 1 -type d -name "Documents_*" \
  -mtime +7 -exec rm -rf {} \;
```

### Health Check Script

```bash
#!/bin/zsh

check_disk() {
  used=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
  if [ "$used" -gt 80 ]; then
    echo "⚠️  Disk usage: ${used}%"
  fi
}

check_memory() {
  free_mem=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
  if [ "$free_mem" -lt 1000000 ]; then
    echo "⚠️  Low memory available"
  fi
}

check_updates() {
  updates=$(softwareupdate -l 2>/dev/null | wc -l)
  if [ "$updates" -gt 0 ]; then
    echo "⚠️  $updates updates available"
  fi
}

check_brew() {
  outdated=$(brew outdated | wc -l)
  if [ "$outdated" -gt 0 ]; then
    echo "ℹ️  $outdated Homebrew packages can be updated"
  fi
}

echo "macOS Health Check"
check_disk
check_memory
check_updates
check_brew
```

## Shortcuts App Patterns

### File Operations

```
Get files from Folder → Filter → Create folder → Move files
```

Create smart file organizer:

1. Get files from Downloads
2. Filter by creation date (within last 7 days)
3. Ask for destination folder
4. Move files to destination
5. Show notification with count

### System Automation

```
Ask for text → Run script → Show result → Send notification
```

Quick command executor:

1. Ask user for shell command
2. Run script (zsh): `[input text]`
3. Display alert with output
4. Log to file

### Calendar Integration

```
Ask for event details → Create calendar event → Show reminder
```

Quick event creator:

1. Ask for event name
2. Ask for date/time
3. Create event in default calendar
4. Send notification

### Text Processing

```
Ask for text → Replace text → Copy to clipboard → Notify
```

Text processor:

1. Ask for input text
2. Replace "find" with "replace"
3. Set clipboard to result
4. Show notification "Copied to clipboard"

## LaunchAgent Configuration (plist)

Create `~/Library/LaunchAgents/com.example.backup.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.example.backup</string>

  <key>ProgramArguments</key>
  <array>
    <string>/Users/you/.local/bin/backup.sh</string>
  </array>

  <key>StartInterval</key>
  <integer>86400</integer>  <!-- Run daily (86400 seconds) -->

  <key>StandardOutPath</key>
  <string>/Users/you/.local/log/backup.log</string>

  <key>StandardErrorPath</key>
  <string>/Users/you/.local/log/backup.err</string>

  <key>RunAtLoad</key>
  <true/>
</dict>
</plist>
```

Load:

```bash
launchctl load ~/Library/LaunchAgents/com.example.backup.plist
```

## VS Code Integration

Automate VS Code with shell scripts:

```bash
#!/bin/zsh

# Open file in VS Code
code /path/to/file.js

# Open folder
code /path/to/project

# Open at line
code -g /path/to/file.js:10:5

# Install extension
code --install-extension biomejs.biome
```

## Git Workflow Automation

```bash
#!/bin/zsh

# Auto-commit script
auto_commit() {
  git add -A
  git commit -m "$(date +%Y-%m-%d\ %H:%M:%S): Auto-commit"
  git push
}

# Sync branches
sync_branches() {
  git fetch origin
  git rebase origin/main
  git push
}

# Create feature branch
create_feature() {
  branch_name="feature/$(date +%s)"
  git checkout -b "$branch_name"
  echo "Created branch: $branch_name"
}
```

## Debugging Tips

### View Logs

```bash
# System logs
log stream --level=debug

# Specific process logs
log stream --predicate 'process == "Finder"'

# LaunchAgent logs
log stream --predicate 'eventMessage contains "com.example"'
```

### Test AppleScript

```bash
# Run AppleScript file
osascript /path/to/script.applescript

# Run inline
osascript -e 'display notification "Hello"'
```

### Test Shell Script

```bash
# Debug mode
zsh -x script.sh

# Check syntax
zsh -n script.sh
```

## Security Considerations

1. Never hardcode passwords in scripts
2. Use `sudo` with user confirmation
3. Store secrets in Keychain:

```bash
# Add to Keychain
security add-generic-password -a username -s "service" -w "password"

# Retrieve from Keychain
security find-generic-password -a username -s "service" -w
```

4. Use proper file permissions:

```bash
chmod 700 ~/.local/bin/private-script.sh
```

5. Sign AppleScripts:

```bash
codesign -s - /path/to/script.applescript
```

## References

- AppleScript reference: https://developer.apple.com/library/archive/documentation/AppleScript/
- macOS scripting: https://developer.apple.com/library/archive/documentation/Miscellaneous/Reference/EntireBook/
- Shortcuts documentation: https://support.apple.com/guide/shortcuts/
- Homebrew: https://brew.sh
