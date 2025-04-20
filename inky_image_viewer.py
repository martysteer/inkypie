#!/usr/bin/env python3
"""
Inky Image Viewer - Display images on Inky displays from local files or URLs.
For the 7-color Inky Impression display.
"""
import sys
import os
import argparse
import time
import requests
from io import BytesIO
from PIL import Image
try:
    from inky.auto import auto
except ImportError:
    print("Please install the Inky library: pip install inky")
    sys.exit(1)

# Get the path to the script's directory
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Display an image on Inky.')
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('--file', type=str, help='Path to local image file')
    source_group.add_argument('--url', type=str, help='URL of image to download')
    parser.add_argument('--rotate', type=int, choices=[0, 90, 180, 270], default=0, 
                      help='Rotate image (degrees)')
    parser.add_argument('--saturation', type=float, default=0.5, 
                      help='Saturation for 7-color displays (0.0 to 1.0)')
    parser.add_argument('--simulation', action='store_true', 
                      help='Simulate display without actual hardware')
    parser.add_argument('--sample', type=int, default=None, 
                      help='Use sample image (1-3) from samples directory')
    parser.add_argument('--verbose', action='store_true', 
                      help='Enable verbose output')
    return parser.parse_args()

def load_image_from_url(url, verbose=False):
    """Load an image from a URL."""
    if verbose:
        print(f"Downloading image from: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return Image.open(BytesIO(response.content))
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        sys.exit(1)
    except IOError as e:
        print(f"Error opening image: {e}")
        sys.exit(1)

def load_image_from_file(path, verbose=False):
    """Load an image from a file."""
    if verbose:
        print(f"Loading image from: {path}")
    
    try:
        return Image.open(path)
    except IOError as e:
        print(f"Error opening image: {e}")
        sys.exit(1)

def prepare_image(image, inky_display, rotation=0, saturation=0.5, verbose=False):
    """Prepare image for display on Inky."""
    if verbose:
        print(f"Original image size: {image.width}x{image.height}")
        print(f"Display size: {inky_display.width}x{inky_display.height}")
    
    # Rotate image if needed
    if rotation:
        image = image.rotate(rotation, expand=True)
    
    # Resize image to fit display while maintaining aspect ratio
    display_width, display_height = inky_display.width, inky_display.height
    image_ratio = image.width / image.height
    display_ratio = display_width / display_height
    
    if image_ratio > display_ratio:
        # Image is wider than display
        new_width = display_width
        new_height = int(display_width / image_ratio)
    else:
        # Image is taller than display
        new_height = display_height
        new_width = int(display_height * image_ratio)
    
    # Resize image
    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    if verbose:
        print(f"Resized image: {image.width}x{image.height}")
    
    # Create a blank canvas the size of the display
    new_image = Image.new("RGBA", (display_width, display_height), (255, 255, 255, 255))
    
    # Calculate position to center image
    x = (display_width - new_width) // 2
    y = (display_height - new_height) // 2
    
    # Paste the image
    new_image.paste(image, (x, y))
    
    # Convert to RGB for compatibility
    return new_image.convert("RGB")

def main():
    args = get_args()
    verbose = args.verbose
    
    # Handle sample images
    if args.sample is not None:
        sample_num = args.sample
        sample_file = os.path.join(SCRIPT_DIR, "samples", f"sample{sample_num}.jpg")
        if not os.path.exists(sample_file):
            print(f"Sample image {sample_num} not found")
            sys.exit(1)
        args.file = sample_file
        if verbose:
            print(f"Using sample image: {sample_file}")
    
    # Set up display
    try:
        if args.simulation:
            # Use mock display with 7-color simulation
            print("Running in simulation mode")
            from inky.mock import InkyMockImpression
            inky_display = InkyMockImpression()
            import atexit
            atexit.register(inky_display.wait_for_window_close)
        else:
            # Use actual display
            inky_display = auto()
            if hasattr(inky_display, 'set_border'):
                inky_display.set_border(inky_display.WHITE)
    except Exception as e:
        print(f"Error initializing display: {e}")
        print("If using hardware, ensure I2C and SPI are enabled with:")
        print("  sudo raspi-config nonint do_i2c 0")
        print("  sudo raspi-config nonint do_spi 0")
        print("  sudo nano /boot/firmware/config.txt (add 'dtoverlay=spi0-0cs')")
        print("Or try with --simulation to test without hardware")
        sys.exit(1)
    
    # Load image
    if args.url:
        image = load_image_from_url(args.url, verbose)
    elif args.file:
        image = load_image_from_file(args.file, verbose)
    
    # Prepare and display image
    processed_image = prepare_image(
        image, 
        inky_display, 
        rotation=args.rotate,
        saturation=args.saturation,
        verbose=verbose
    )
    
    if verbose:
        print("Processing image for display...")
    
    # Different display types have different methods
    if hasattr(inky_display, 'set_image'):
        if 'saturation' in inky_display.set_image.__code__.co_varnames:
            # For 7-color displays that support saturation
            inky_display.set_image(processed_image, saturation=args.saturation)
        else:
            # For other displays
            inky_display.set_image(processed_image)
    
    if verbose:
        print("Updating display...")
    
    # Update the display
    start_time = time.time()
    inky_display.show()
    elapsed = time.time() - start_time
    
    if verbose:
        print(f"Display updated in {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
