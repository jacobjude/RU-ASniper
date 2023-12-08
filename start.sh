#!/bin/bash

echo "Starting Rutgers AutoSniper setup..."

# Check if the virtual environment directory exists, if not create it
if [ ! -d ".venv" ]; then
   echo "Creating a Python virtual environment in the current directory..."
   python3 -m venv .venv
   source .venv/bin/activate
   echo "Installing dependencies from requirements.txt..."
   python3 -m pip install --upgrade pip
   pip install -r requirements.txt
else
   echo "Activating the virtual environment..."
   source .venv/bin/activate
fi

# Run the Python program in the ./src/configure.py directory
python3 ./src/configure.py

# Ask the user if they want to hide the browser window
read -p "Would you like to hide the browser window? (y/n): " hide
if [ "$hide" == "y" ]; then
   args=""
else
   args="--browser"
fi

# Run the appropriate Python script based on the user's choice
python3 ./src/sniper.py $args
