#!/bin/bash
# Setup script for User Data Viewer GUI virtual environment

echo "Setting up Python virtual environment for User Data Viewer GUI..."

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo ""
echo "Virtual environment setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the GUI application, run:"
echo "  python user_data_viewer.py"
echo ""
