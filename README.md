# InkyPie

A collection of improved utilities for Pimoroni Inky e-paper displays.

## Inky Image Viewer

This script allows you to display images on your Inky display from either local files or URLs.

### Features

- Support for URL-based images (downloads from the web)
- Automatic image resizing and centering on the display
- Support for various display types, with special handling for 7-color displays
- Simulation mode for testing without hardware
- Sample image support
- Rotation options
- Adjustable saturation for 7-color displays

### Installation

Make sure you have the required dependencies:

```bash
pip install inky pillow requests
```

### Usage

Basic usage:

```bash
# Display an image from a URL
python3 inky_image_viewer.py --url https://example.com/image.jpg

# Display a local image file
python3 inky_image_viewer.py --file /path/to/image.jpg

# Use simulation mode (no hardware required)
python3 inky_image_viewer.py --url https://example.com/image.jpg --simulation

# Rotate the image
python3 inky_image_viewer.py --url https://example.com/image.jpg --rotate 90

# Adjust saturation (for 7-color displays, 0.0 to 1.0)
python3 inky_image_viewer.py --url https://example.com/image.jpg --saturation 0.7

# Display a sample image (if available in the samples directory)
python3 inky_image_viewer.py --sample 1

# Enable verbose output to see details of the process
python3 inky_image_viewer.py --url https://example.com/image.jpg --verbose
```

### Troubleshooting

If you encounter issues with hardware detection:

1. Make sure I2C and SPI are enabled:
   ```bash
   sudo raspi-config nonint do_i2c 0
   sudo raspi-config nonint do_spi 0
   ```

2. Add the following to `/boot/firmware/config.txt`:
   ```
   dtoverlay=spi0-0cs
   ```

3. Try using the `--simulation` flag to test without hardware.

### Adding Sample Images

Place sample images in the `samples` directory with names like `sample1.jpg`, `sample2.jpg`, etc.
Then use `--sample 1` to display the first sample image.
