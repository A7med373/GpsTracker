#!/bin/bash
# Simple script to run the GF22 GPS Tracker web service in development mode

echo "Starting GF22 GPS Tracker web service..."
echo "Press Ctrl+C to stop the service"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed or not in PATH"
    exit 1
fi

# Check if requirements are installed
echo "Checking dependencies..."
pip3 install -r requirements.txt

# Run the application
echo "Starting the application..."
python3 app.py