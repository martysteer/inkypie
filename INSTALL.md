# InkyPie - Inky Display Image Viewer

A simple Python script for displaying and manipulating images on Inky e-ink displays using the side buttons for control.

## Features

- Display images from local files or URLs
- Control image scale, rotation, and aspect ratio via buttons
- Automatic detection of display type
- Support for all Inky display types (pHAT, wHAT, and Impression)

## Requirements

- Raspberry Pi with an Inky display connected
- Python 3
- Inky library and dependencies (see Installation)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/inkypie.git
cd inkypie
```

2. Install dependencies:
```bash
pip3 install inky[rpi] pillow
```

3. Make the script executable:
```bash
chmod +x inky_image_viewer.py
```

## Usage

Run the script with a URL or path to an image:

```bash
python3 inky_image_viewer.py --url https://example.com/image.jpg
```

Or with a local file:

```bash
python3 inky_image_viewer.py --url /path/to/your/image.jpg
```

### Button Controls

- **Button A**: Increase scale
- **Button B**: Decrease scale  
- **Button C**: Rotate by 90°
- **Button D**: Toggle aspect ratio preservation

Press CTRL+C to exit.

## Customization

You can modify the `BUTTONS` list in the script if your buttons are connected to different GPIO pins.

## Git Project Integration

This project is designed to work with Git for version control. Here's how to manage it:

### Initial Setup

If you've just created this project, initialize a git repository:

```bash
git init
git add inky_image_viewer.py README.md
git commit -m "Initial commit with image viewer script"
```

### Connecting to GitHub

1. Create a repository on GitHub
2. Connect your local repository:

```bash
git remote add origin https://github.com/yourusername/inkypie.git
git branch -M main
git push -u origin main
```

### Workflow for Updates

When making changes:

1. Edit your files
2. Test your changes
3. Stage and commit:
```bash
git add .
git commit -m "Description of changes"
git push
```

### Synchronizing with Raspberry Pi

To get your code onto your Raspberry Pi:

1. On your Raspberry Pi:
```bash
git clone https://github.com/yourusername/inkypie.git
```

2. For future updates:
```bash
cd inkypie
git pull
```

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Pimoroni for their excellent Inky library
- The Raspberry Pi community
