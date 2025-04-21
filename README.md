# InkyPie

A collection of improved utilities for Pimoroni Inky e-paper displays, with enhanced cross-platform compatibility.

## Inky Image Viewer

This script allows you to display images on your Inky display from either local files or URLs, with full cross-platform support.

### Features

- **Cross-Platform Compatibility**: Develop on any platform, deploy on Raspberry Pi
- **Automatic Hardware/Simulator Detection**: Uses real hardware on Raspberry Pi, simulator elsewhere
- **Supports All Inky Displays**: pHAT, wHAT, SSD1608, Impression, and more
- **Image Source Options**: Display images from URLs, local files, or galleries
- **Button Controls**: Navigate images and control display via buttons or simulator keys
- **Dynamic Resizing**: Automatically resizes and centers images on the display
- **Rotation Support**: Rotate images in 90° increments
- **Saturation Control**: Adjustable color saturation for 7-color displays
- **Simulation Mode**: Test without hardware even on Raspberry Pi

### Installation

Make sure you have the required dependencies:

```bash
# Full installation with simulator support
pip install inky pillow requests pygame

# Minimal installation (hardware support only)
pip install inky pillow requests
```

### Basic Usage

```bash
# Display an image from a URL on auto-detected display
python inky_image_viewer.py --url https://example.com/image.jpg

# Display a local image file on specific display type
python inky_image_viewer.py --type impressions --file /path/to/image.jpg

# Use simulation mode (no hardware required)
python inky_image_viewer.py --url https://example.com/image.jpg --simulation

# Display a gallery of images from a text file
python inky_image_viewer.py --gallery-file sample_gallery.txt

# Rotate the image
python inky_image_viewer.py --url https://example.com/image.jpg --rotate 90

# Adjust saturation (for 7-color displays, 0.0 to 1.0)
python inky_image_viewer.py --url https://example.com/image.jpg --saturation 0.7

# Display a sample image (if available in the samples directory)
python inky_image_viewer.py --sample 1

# Enable verbose output to see details of the process
python inky_image_viewer.py --url https://example.com/image.jpg --verbose
```

### Button Controls

When using hardware buttons on Raspberry Pi or keys in simulator mode:
- **A / A key**: Previous image
- **B / B key**: Next image
- **C / C key**: Rotate counter-clockwise
- **D / D key**: Rotate clockwise

### Adding Sample Images

Place sample images in the `samples` directory with names like `sample1.jpg`, `sample2.jpg`, etc.
Then use `--sample 1` to display the first sample image.

## Cross-Platform Development

The enhanced Inky library now supports seamless development across platforms:

- **Develop on any platform**: Mac, Windows, Linux
- **Deploy to Raspberry Pi**: Same code works without changes
- **Debug with simulator**: Visualize e-ink display behavior

For more details on cross-platform development, see [README-platform-update.md](README-platform-update.md).

### Development Tools

The new library includes powerful development tools:

```python
from inky import auto
from inky.debug import InkyDebugger, FastModeEnabler

# Get an Inky display
inky = auto()

# Add debugging capabilities
debugger = InkyDebugger(inky)
debugger.toggle_grid()  # Show grid overlay
debugger.print_display_info()  # Display information

# Enable fast mode for rapid development (bypasses e-ink timing)
fast_mode = FastModeEnabler(inky)
fast_mode.enable()

# Display a test pattern showing all available colors
debugger.draw_test_pattern()
```

## Setting Up Hardware

If you're using actual Inky hardware, ensure:

1. I2C and SPI are enabled:
   ```bash
   sudo raspi-config nonint do_i2c 0
   sudo raspi-config nonint do_spi 0
   ```

2. Add the following to `/boot/firmware/config.txt`:
   ```
   dtoverlay=spi0-0cs
   ```

3. Install required dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip python3-pil python3-requests
   pip3 install inky
   ```

## Example Scripts

Check out these examples:
- `examples/cross_platform.py` - Cross-platform development example
- `examples/7color/*` - Examples for 7-color Inky Impression displays
- `examples/what/*` - Examples for Inky wHAT displays

## Troubleshooting

If you encounter issues:

1. **Check Hardware Connections**: Ensure the display is properly connected
2. **Try Simulation Mode**: Use `--simulation` to test without hardware
3. **Specify Display Type**: Use `--type` and `--color` if auto-detection fails
4. **Enable Verbose Output**: Use `--verbose` for detailed debugging information

For more help, check the [Pimoroni Inky GitHub repository](https://github.com/pimoroni/inky).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
