#!/bin/bash
# setup.sh - Setup script for InkyPie

echo "Setting up InkyPie..."
echo "====================="

# Check if running on Raspberry Pi
if [ ! -e /proc/device-tree/model ]; then
    echo "Error: This script must be run on a Raspberry Pi."
    exit 1
fi

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo:"
    echo "sudo ./setup.sh"
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Installing Python 3..."
    apt-get update
    apt-get install -y python3 python3-pip
else
    echo "✓ Python 3 is installed"
fi

# Ensure SPI and I2C are enabled
echo "Enabling SPI and I2C interfaces..."
raspi-config nonint do_spi 0
raspi-config nonint do_i2c 0

# Add SPI chip select fix to config.txt if not already present
if ! grep -q "dtoverlay=spi0-0cs" /boot/firmware/config.txt; then
    echo "Adding SPI chip select fix to config.txt..."
    echo "dtoverlay=spi0-0cs" >> /boot/firmware/config.txt
    echo "✓ Added SPI chip select fix"
else
    echo "✓ SPI chip select fix already configured"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$HOME/.virtualenvs/inkypie" ]; then
    echo "Creating virtual environment..."
    pip3 install virtualenv
    python3 -m virtualenv "$HOME/.virtualenvs/inkypie"
    echo "✓ Created virtual environment"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment and install requirements
echo "Installing dependencies..."
source "$HOME/.virtualenvs/inkypie/bin/activate"
pip install -r requirements.txt

# Make the script executable
chmod +x inky_image_viewer.py

echo ""
echo "Setup complete! You can now use InkyPie."
echo ""
echo "To activate the virtual environment:"
echo "source $HOME/.virtualenvs/inkypie/bin/activate"
echo ""
echo "To run the image viewer:"
echo "python3 inky_image_viewer.py --url [image_url_or_path]"
echo ""
echo "A reboot is recommended to ensure all settings take effect."
echo "Would you like to reboot now? (y/n)"
read answer

if [ "$answer" == "y" ] || [ "$answer" == "Y" ]; then
    echo "Rebooting..."
    reboot
fi
