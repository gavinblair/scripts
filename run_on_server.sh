#!/bin/bash

# this is for running a php on a specific pantheon environment

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <site> <environment> <php_file>"
    exit 1
fi

# Assign arguments to variables for readability
SITE=$1
ENVIRONMENT=$2
PHP_FILE=$3

# Check if the specified PHP file exists
if [ ! -f "$PHP_FILE" ]; then
    echo "Error: PHP file '$PHP_FILE' not found."
    exit 1
fi

# Convert environment to lowercase for case-insensitive comparison
ENVIRONMENT_LOWER=$(echo "$ENVIRONMENT" | tr '[:upper:]' '[:lower:]')

# Set default confirmation response based on environment
if [ "$ENVIRONMENT_LOWER" == "live" ]; then
    DEFAULT="N"
    MESSAGE="YOU ARE ABOUT TO RUN THIS SCRIPT ON THE 'LIVE' ENVIRONMENT."
else
    DEFAULT="Y"
    MESSAGE="You are about to run this script on the '$ENVIRONMENT' environment."
fi

# Dynamically format prompt based on the default
if [ "$DEFAULT" == "Y" ]; then
    PROMPT="(Y/n)"
else
    PROMPT="(y/N)"
fi

# Prompt user for confirmation with line breaks
echo ""
echo "$MESSAGE"
echo ""
read -p "Proceed? $PROMPT [default: $DEFAULT]: " RESPONSE
echo ""

# Use default if no response is provided
RESPONSE=${RESPONSE:-$DEFAULT}

# Convert response to uppercase for case-insensitive comparison
RESPONSE=$(echo "$RESPONSE" | tr '[:lower:]' '[:upper:]')

if [ "$RESPONSE" != "Y" ]; then
    echo "Operation cancelled by user."
    echo ""
    exit 0
fi

# Construct and execute the command
COMMAND="terminus drush $SITE.$ENVIRONMENT -- php-eval \"\$(cat $PHP_FILE)\""
echo "Running command: $COMMAND"
echo ""
eval $COMMAND
