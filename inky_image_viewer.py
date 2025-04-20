#!/usr/bin/env python3
# inky_image_viewer.py - Display images on Inky with button controls

import os
import argparse
import time
import urllib.request
from io import BytesIO
from PIL import Image
import RPi.GPIO as GPIO
from inky.auto import auto

# Optional imports for extended functionality
# Uncomment as needed for additional features
# try:
#     import requests  # More robust URL handling
#     USE_REQUESTS = True
# except ImportError:
#     USE_REQUESTS = False
#
# try:
#     from PIL import ImageDraw, ImageFont  # For text overlay feature
#     TEXT_OVERLAY_AVAILABLE = True
# except ImportError:
#     TEXT_OVERLAY_AVAILABLE = False

# Button pins (adjust if your buttons are connected differently)
BUTTONS = [5, 6, 16, 24]  # Typical button pins for Inky pHAT/wHAT
NAMES = ["A", "B", "C", "D"]  # Names for the buttons

# Display settings
scale = 1.0
rotation = 0
preserve_aspect_ratio = True

# Get the Inky display
inky_display = auto()
WIDTH, HEIGHT = inky_display.resolution

def setup_gpio():
    """Set up GPIO for button inputs."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    for pin in BUTTONS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
    print("GPIO set up for buttons.")

def download_image(url):
    """Download an image from a URL or load from local file."""
    try:
        if os.path.isfile(url):  # Local file
            return Image.open(url)
        
        # Remote URL
        # Use requests if available for better error handling
        if 'USE_REQUESTS' in globals() and USE_REQUESTS:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        else:
            # Fallback to urllib
            response = urllib.request.urlopen(url)
            image_data = response.read()
            return Image.open(BytesIO(image_data))
    except Exception as e:
        print(f"Error loading image: {e}")
        exit(1)

def process_image(image):
    """Process and prepare image for display on Inky."""
    # Resize image based on current settings
    img_width, img_height = image.size
    
    if preserve_aspect_ratio:
        # Calculate aspect-preserved size
        ratio = min(WIDTH / img_width, HEIGHT / img_height) * scale
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
    else:
        # Scale directly
        new_width = int(WIDTH * scale)
        new_height = int(HEIGHT * scale)
    
    # Resize the image
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    
    # Create a blank white image of the Inky's dimensions
    final_image = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 255))
    
    # Calculate paste position (center)
    paste_x = (WIDTH - new_width) // 2
    paste_y = (HEIGHT - new_height) // 2
    
    # Paste resized image onto blank background
    final_image.paste(resized_image, (paste_x, paste_y))
    
    # Rotate if needed
    if rotation != 0:
        final_image = final_image.rotate(rotation, expand=False)
    
    # Convert to palette mode for Inky
    if hasattr(inky_display, 'set_image'):
        # For Inky Impression (7-color)
        if hasattr(inky_display, 'DESATURATED_PALETTE'):
            return final_image
        # For standard Inky
        else:
            return final_image.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=3)
    
    return final_image.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=3)

def update_display(image):
    """Update the Inky display with the current image."""
    try:
        processed_image = process_image(image)
        
        # Check if we have a 7-color Inky Impression
        if hasattr(inky_display, 'set_image') and hasattr(inky_display, 'DESATURATED_PALETTE'):
            inky_display.set_image(processed_image, saturation=0.5)
        else:
            inky_display.set_image(processed_image)
            
        inky_display.show()
        print("Display updated.")
    except Exception as e:
        print(f"Error updating display: {e}")

def handle_button_press(channel, image):
    """Handle button presses to modify display settings."""
    global scale, rotation, preserve_aspect_ratio
    
    index = BUTTONS.index(channel)
    name = NAMES[index]
    
    if name == "A":  # Scale up
        scale = min(scale + 0.1, 2.0)
        print(f"Scale increased to: {scale:.1f}")
    elif name == "B":  # Scale down
        scale = max(scale - 0.1, 0.1)
        print(f"Scale decreased to: {scale:.1f}")
    elif name == "C":  # Rotate
        rotation = (rotation + 90) % 360
        print(f"Rotation set to: {rotation}°")
    elif name == "D":  # Toggle aspect ratio
        preserve_aspect_ratio = not preserve_aspect_ratio
        print(f"Preserve aspect ratio: {preserve_aspect_ratio}")
    
    update_display(image)
    time.sleep(0.2)  # Debounce

def main():
    """Main function to run the image viewer."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Display an image from URL on Inky")
    parser.add_argument("--url", required=True, help="URL or path to the image file")
    args = parser.parse_args()
    
    # Download and prepare the image
    print(f"Loading image from: {args.url}")
    original_image = download_image(args.url)
    
    # Set up GPIO for buttons
    setup_gpio()
    
    # Display the initial image
    update_display(original_image)
    
    # Set up button callbacks
    # Using a function factory to avoid lambda closure issues
    def make_callback(pin_param, img):
        return lambda channel: handle_button_press(pin_param, img)
        
    for pin in BUTTONS:
        GPIO.add_event_detect(pin, GPIO.FALLING, 
                             callback=make_callback(pin, original_image),
                             bouncetime=200)
    
    print("\nControls:")
    print("Button A: Increase scale")
    print("Button B: Decrease scale")
    print("Button C: Rotate 90°")
    print("Button D: Toggle aspect ratio preservation")
    print("\nPress CTRL+C to exit.")
    
    # Keep the program running
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
