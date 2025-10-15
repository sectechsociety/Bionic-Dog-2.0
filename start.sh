#!/bin/bash
echo "🐕 Enhanced Bionic Dog Controller 2.0 🤖"
echo "Starting up..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python is not installed or not in PATH"
        echo "Please install Python 3.7+ from https://python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Run the startup script
$PYTHON_CMD run.py
