#!/bin/bash

# Function to show usage information
usage() {
    echo "Usage: $0 [-t <HH:MM>] <minutes> <message>"
    exit 1
}

# Default target_time to current time
target_time=""

# Parse options
while getopts ":t:" opt; do
    case ${opt} in
        t )
            target_time=$OPTARG
            ;;
        \? )
            usage
            ;;
    esac
done
shift $((OPTIND -1))

# Check if the correct number of arguments is provided
if [ -z "$target_time" ] && [ "$#" -ne 2 ]; then
    usage
elif [ -n "$target_time" ] && [ "$#" -ne 1 ]; then
    usage
fi

# Calculate the target time
if [ -n "$target_time" ]; then
    # Get current date and append the target time
    target_date=$(date +%Y-%m-%d)
    target_time=$(date -j -f "%Y-%m-%d %H:%M" "$target_date $target_time" +%s)
else
    # Check if the first argument is a valid number
    if ! [[ $1 =~ ^[0-9]+$ ]]; then
        echo "Error: First argument must be a positive integer."
        exit 1
    fi
    # Calculate the target time in seconds since epoch
    target_time=$(($(date +%s) + $1 * 60))
    shift
fi

# Wait until the current time reaches or surpasses the target time
while [ $(date +%s) -lt $target_time ]; do
    sleep 1
done

# Output the message and trigger the reminder
echo "$1"
/Users/gavinblair/Projects/apps/beep.sh
/Users/gavinblair/Projects/apps/toast.sh "$1" "Reminder"

