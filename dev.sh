#!/bin/bash

# Kill any existing Flask processes
pkill -f "python run.py"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install or update dependencies
pip install -r requirements.txt

# Run Flask application
python run.py 