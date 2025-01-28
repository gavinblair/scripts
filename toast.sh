#!/bin/bash

# Set the title for the notification
if [ -z "$2" ]; then
    title="Notification"
else
    title="$2"
fi

# Set the app for the notification icon if specified
if [ -n "$3" ]; then
    app_icon="$3"
else
    app_icon="Finder"  # Default app if none is specified
fi

# Use terminal-notifier to display notification with the app icon
terminal-notifier -message "$1" -title "$title" -sender "com.apple.$app_icon"

