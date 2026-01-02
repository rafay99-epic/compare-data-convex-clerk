#!/bin/bash
# Quick launcher script for the Data Explorer application

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the application
python -m app.main
