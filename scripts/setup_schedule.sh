#!/bin/bash

# Setup Script for Daily Brief 10:00 AM Weekday Schedule on macOS

PROJECT_DIR="/Users/mdmehedihassan/Desktop/daily-brief"
PLIST_FILE="$HOME/Library/LaunchAgents/com.dailybrief.schedule.plist"

echo "⏰ Installing Daily Brief 10:00 AM Weekday Schedule (Monday - Friday)..."

cat <<EOF > "$PLIST_FILE"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dailybrief.schedule</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/osascript</string>
        <string>-e</string>
        <string>display notification "Your Daily Brief is ready for today!" with title "☀️ 10:00 AM Daily Brief" sound name "Glass"</string>
        <string>-e</string>
        <string>open location "http://localhost:8090"</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Weekday</key>
            <integer>1</integer>
            <key>Hour</key>
            <integer>10</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <dict>
            <key>Weekday</key>
            <integer>2</integer>
            <key>Hour</key>
            <integer>10</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <dict>
            <key>Weekday</key>
            <integer>3</integer>
            <key>Hour</key>
            <integer>10</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <dict>
            <key>Weekday</key>
            <integer>4</integer>
            <key>Hour</key>
            <integer>10</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <dict>
            <key>Weekday</key>
            <integer>5</integer>
            <key>Hour</key>
            <integer>10</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>
</dict>
</plist>
EOF

launchctl unload "$PLIST_FILE" 2>/dev/null
launchctl load "$PLIST_FILE"

echo "✅ 10:00 AM Weekday Schedule successfully installed!"
echo "   It will trigger a desktop notification and open http://localhost:8090 every Monday through Friday at 10:00 AM."
