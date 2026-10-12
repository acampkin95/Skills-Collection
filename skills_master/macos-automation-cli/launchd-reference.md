# LaunchAgent Configuration Reference

Complete reference for launchd plist configuration on macOS.

## Property List Structure

LaunchAgent plists use XML with specific keys:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.example.agent</string>
    <!-- Other keys -->
</dict>
</plist>
```

## Required Keys

### Label
Unique identifier for the job.
```xml
<key>Label</key>
<string>com.example.myagent</string>
```

## Common Optional Keys

### Program and Arguments
```xml
<key>Program</key>
<string>/usr/bin/python3</string>

<key>ProgramArguments</key>
<array>
    <string>python3</string>
    <string>/path/to/script.py</string>
</array>
```

### Run at Load
Start immediately when loaded.
```xml
<key>RunAtLoad</key>
<true/>
```

### Keep Alive
Restart if process exits.
```xml
<key>KeepAlive</key>
<true/>

<!-- Or with conditions -->
<key>KeepAlive</key>
<dict>
    <key>SuccessfulExit</key>
    <false/>
</dict>
```

### Run on Demand
Only run when explicitly requested.
```xml
<key>RunAtLoad</key>
<false/>
<key>KeepAlive</key>
<false/>
```

### Start Interval
Run every N seconds.
```xml
<key>StartInterval</key>
<integer>300</integer>
```

### Start Calendar Interval
Run at specific times.
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>9</integer>
    <key>Minute</key>
    <integer>30</integer>
</dict>
```

### Working Directory
```xml
<key>WorkingDirectory</key>
    <string>/Users/username/project</string>
```

### Environment Variables
```xml
<key>EnvironmentVariables</key>
<dict>
    <key>PATH</key>
    <string>/usr/local/bin:/usr/bin:/bin</string>
    <key>PYTHONPATH</key>
    <string>/Users/username/lib</string>
</dict>
```

### Standard Output and Error
```xml
<key>StandardOutPath</key>
<string>/Users/username/logs/agent.log</string>

<key>StandardErrorPath</key>
<string>/Users/username/logs/agent.err</string>
```

### User and Group
```xml
<key>UserName</key>
<string>username</string>

<key>GroupName</key>
<string>staff</string>
```

### Root Directory
```xml
<key>RootDirectory</key>
<string>/var/root</string>
```

## Advanced Options

### Watch Paths
Restart when files change.
```xml
<key>WatchPaths</key>
<array>
    <string>/Users/username/config/</string>
    <string>/Users/username/project/*.py</string>
</array>
```

### Queue Directories
Monitor directory contents.
```xml
<key>QueueDirectories</key>
<array>
    <string>/Users/username/incoming/</string>
</array>
```

### Launch Only Once
```xml
<key>LaunchOnlyOnce</key>
<true/>
```

### Throttle Interval
Minimum time between launches.
```xml
<key>ThrottleInterval</key>
<integer>10</integer>
```

### Exit Time Out
Wait for graceful shutdown.
```xml
<key>ExitTimeOut</key>
<integer>30</integer>
```

## Example: Background Sync Agent

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.example.syncagent</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/username/bin/sync.py</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <false/>

    <key>StartInterval</key>
    <integer>3600</integer>

    <key>WorkingDirectory</key>
    <string>/Users/username</string>

    <key>StandardOutPath</key>
    <string>/Users/username/logs/sync.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/username/logs/sync.err</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONPATH</key>
        <string>/Users/username/lib</string>
    </dict>
</dict>
</plist>
```

## Management Commands

### User Agents
```bash
# Load agent
launchctl load ~/Library/LaunchAgents/com.example.agent.plist

# Unload agent
launchctl unload ~/Library/LaunchAgents/com.example.agent.plist

# Start agent
launchctl start com.example.agent

# Stop agent
launchctl stop com.example.agent

# List loaded
launchctl list

# View stderr/stdout
tail -f /Users/username/logs/agent.log
```

### System Daemons
```bash
# Load (requires sudo)
sudo launchctl load /Library/LaunchDaemons/com.example.daemon.plist

# Unload (requires sudo)
sudo launchctl unload /Library/LaunchDaemons/com.example.daemon.plist
```

## Debugging

### Enable Debug Logging
```bash
# Enable debug mode
sudo launchctl log level debug

# View logs
log show --predicate 'process == "launchd"' --info
```

### Check Status
```bash
# Check if running
launchctl list | grep com.example.agent

# Check stderr
cat /var/log/system.log | grep com.example.agent
```

## Disabled Flag

To prevent a plist from loading:
```bash
# Disable
defaults write /path/to/agent.plist Disabled -bool true

# Enable
defaults delete /path/to/agent.plist Disabled
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Agent not running | Check `launchctl list` for errors |
| Permission denied | Ensure correct UserName or run as user |
| Restart loops | Check KeepAlive settings |
| Missing PATH | Set in EnvironmentVariables |
| File not found | Use absolute paths, check WorkingDirectory |
