#!/usr/bin/env python3
"""
Inky Image Viewer - Display images on Inky displays from local files or URLs.
For the 7-color Inky Impression display.
Supports gallery mode with button navigation.
"""
import sys
import os
import argparse
import time
import requests
import threading
import signal
from io import BytesIO
from PIL import Image

try:
    import gpiod
    import gpiodevice
    from gpiod.line import Bias, Direction, Edge
    BUTTON_SUPPORT = True
except ImportError:
    BUTTON_SUPPORT = False
    print("Warning: gpiod not available. Button support disabled.")

try:
    from inky.auto import auto
except ImportError:
    print("Please install the Inky library: pip install inky")
    sys.exit(1)

# Get the path to the script's directory
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# GPIO pins for buttons (from top to bottom)
# These will vary depending on platform 
# A, B, C, D buttons
BUTTONS = [5, 6, 16, 24]
LABELS = ["A", "B", "C", "D"]

# Button functions
# A: Previous image
# B: Next image
# C: Rotate left (counter-clockwise)
# D: Rotate right (clockwise)

class GalleryViewer:
    """Class to handle gallery viewing with button controls."""
    
    def __init__(self, inky_display, image_urls=None, image_files=None, 
                 saturation=0.5, verbose=False, simulation=False):
        """Initialize the gallery viewer."""
        self.inky_display = inky_display
        self.image_urls = image_urls or []
        self.image_files = image_files or []
        self.saturation = saturation
        self.verbose = verbose
        self.simulation = simulation
        self.current_index = 0
        self.rotation = 0
        self.running = True
        self.button_thread = None
        self.last_button_time = 0
        self.debounce_time = 0.5  # seconds
        
        # Set up buttons if available and not in simulation mode
        if BUTTON_SUPPORT and not simulation:
            self.setup_buttons()
    
    def setup_buttons(self):
        """Set up button handling."""
        try:
            # Create settings for input pins
            input_settings = gpiod.LineSettings(
                direction=Direction.INPUT, 
                bias=Bias.PULL_UP, 
                edge_detection=Edge.FALLING
            )
            
            # Find the GPIO chip
            self.chip = gpiodevice.find_chip_by_platform()
            
            # Build configuration for each button
            self.offsets = [self.chip.line_offset_from_id(id) for id in BUTTONS]
            line_config = dict.fromkeys(self.offsets, input_settings)
            
            # Request the lines
            self.request = self.chip.request_lines(consumer="inky-gallery", config=line_config)
            
            # Start button handling thread
            self.button_thread = threading.Thread(target=self.button_handler, daemon=True)
            self.button_thread.start()
            
            if self.verbose:
                print("Button controls enabled:")
                print("  A: Previous image")
                print("  B: Next image")
                print("  C: Rotate counter-clockwise")
                print("  D: Rotate clockwise")
                
        except Exception as e:
            print(f"Error setting up buttons: {e}")
            print("Button controls disabled")
    
    def button_handler(self):
        """Handle button presses in a separate thread."""
        while self.running:
            try:
                for event in self.request.read_edge_events():
                    self.handle_button_press(event)
            except Exception as e:
                if self.verbose:
                    print(f"Button error: {e}")
                time.sleep(0.1)
    
    def handle_button_press(self, event):
        """Process button press events."""
        # Implement debounce
        current_time = time.time()
        if current_time - self.last_button_time < self.debounce_time:
            return
        
        self.last_button_time = current_time
        
        try:
            index = self.offsets.index(event.line_offset)
            label = LABELS[index]
            
            if self.verbose:
                print(f"Button {label} pressed")
            
            # Handle button actions
            if label == "A":  # Previous image
                self.show_previous()
            elif label == "B":  # Next image
                self.show_next()
            elif label == "C":  # Rotate left
                self.rotate_left()
            elif label == "D":  # Rotate right
                self.rotate_right()
                
        except Exception as e:
            if self.verbose:
                print(f"Error handling button: {e}")
    
    def show_previous(self):
        """Show the previous image in the gallery."""
        total_images = len(self.image_urls) + len(self.image_files)
        if total_images > 0:
            self.current_index = (self.current_index - 1) % total_images
            self.show_current()
    
    def show_next(self):
        """Show the next image in the gallery."""
        total_images = len(self.image_urls) + len(self.image_files)
        if total_images > 0:
            self.current_index = (self.current_index + 1) % total_images
            self.show_current()
    
    def rotate_left(self):
        """Rotate the current image counter-clockwise."""
        self.rotation = (self.rotation - 90) % 360
        self.show_current()
    
    def rotate_right(self):
        """Rotate the current image clockwise."""
        self.rotation = (self.rotation + 90) % 360
        self.show_current()
    
    def get_current_image_source(self):
        """Get the source for the current image (URL or file path)."""
        url_count = len(self.image_urls)
        if self.current_index < url_count:
            return {"url": self.image_urls[self.current_index]}
        else:
            file_index = self.current_index - url_count
            return {"file": self.image_files[file_index]}
    
    def load_current_image(self):
        """Load the current image based on index."""
        source = self.get_current_image_source()
        
        if "url" in source:
            return load_image_from_url(source["url"], self.verbose)
        elif "file" in source:
            return load_image_from_file(source["file"], self.verbose)
    
    def show_current(self):
        """Display the current image with current rotation."""
        if self.verbose:
            print(f"Showing image {self.current_index + 1}/{len(self.image_urls) + len(self.image_files)}")
            source = self.get_current_image_source()
            if "url" in source:
                print(f"URL: {source['url']}")
            else:
                print(f"File: {source['file']}")
            print(f"Rotation: {self.rotation}°")
        
        # Load and display image
        try:
            image = self.load_current_image()
            self.display_image(image)
        except Exception as e:
            print(f"Error loading image: {e}")
    
    def display_image(self, image):
        """Prepare and display an image on the Inky display."""
        processed_image = prepare_image(
            image, 
            self.inky_display, 
            rotation=self.rotation,
            saturation=self.saturation,
            verbose=self.verbose
        )
        
        if self.verbose:
            print("Processing image for display...")
        
        # Different display types have different methods
        if hasattr(self.inky_display, 'set_image'):
            if 'saturation' in self.inky_display.set_image.__code__.co_varnames:
                # For 7-color displays that support saturation
                self.inky_display.set_image(processed_image, saturation=self.saturation)
            else:
                # For other displays
                self.inky_display.set_image(processed_image)
        
        if self.verbose:
            print("Updating display...")
        
        # Update the display
        start_time = time.time()
        self.inky_display.show()
        elapsed = time.time() - start_time
        
        if self.verbose:
            print(f"Display updated in {elapsed:.2f} seconds")
    
    def start(self):
        """Start the gallery viewer with the first image."""
        if len(self.image_urls) + len(self.image_files) > 0:
            self.show_current()
        else:
            print("No images to display")
    
    def stop(self):
        """Clean up resources."""
        self.running = False
        if self.button_thread:
            self.button_thread.join(timeout=1.0)

def get_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Display images on Inky.')
    
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('--file', type=str, help='Path to local image file')
    source_group.add_argument('--url', type=str, help='URL of image to download')
    source_group.add_argument('--gallery-file', type=str, help='Path to text file with list of image URLs')
    source_group.add_argument('--sample', type=int, help='Use sample image (1-3) from samples directory')
    
    parser.add_argument('--rotate', type=int, choices=[0, 90, 180, 270], default=0, 
                      help='Initial rotation (degrees)')
    parser.add_argument('--saturation', type=float, default=0.5, 
                      help='Saturation for 7-color displays (0.0 to 1.0)')
    parser.add_argument('--simulation', action='store_true', 
                      help='Simulate display without actual hardware')
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
        raise
    except IOError as e:
        print(f"Error opening image: {e}")
        raise

def load_image_from_file(path, verbose=False):
    """Load an image from a file."""
    if verbose:
        print(f"Loading image from: {path}")
    
    try:
        return Image.open(path)
    except IOError as e:
        print(f"Error opening image: {e}")
        raise

def load_urls_from_file(file_path, verbose=False):
    """Load a list of URLs from a text file."""
    if verbose:
        print(f"Loading URLs from: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            # Read lines and strip whitespace, filter out empty lines and comments
            urls = [line.strip() for line in f.readlines()]
            urls = [url for url in urls if url and not url.startswith('#')]
            
            if verbose:
                print(f"Loaded {len(urls)} URLs")
            
            return urls
    except IOError as e:
        print(f"Error opening URL file: {e}")
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

def signal_handler(sig, frame):
    """Handle Ctrl+C to exit gracefully."""
    print("Exiting...")
    sys.exit(0)

def main():
    # Set up signal handler for clean exit
    signal.signal(signal.SIGINT, signal_handler)
    
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
    
    image_urls = []
    image_files = []
    
    # Load images based on arguments
    if args.gallery_file:
        # Load gallery of URLs from file
        image_urls = load_urls_from_file(args.gallery_file, verbose)
    elif args.url:
        # Single URL
        image_urls = [args.url]
    elif args.file:
        # Single file
        image_files = [args.file]
    
    # Create gallery viewer
    gallery = GalleryViewer(
        inky_display=inky_display,
        image_urls=image_urls,
        image_files=image_files,
        saturation=args.saturation,
        verbose=verbose,
        simulation=args.simulation
    )
    
    # Set initial rotation
    gallery.rotation = args.rotate
    
    # Start gallery
    try:
        gallery.start()
        
        # For simulation mode or when using gallery, 
        # we need to keep the main thread running
        if args.simulation or args.gallery_file:
            print("Press Ctrl+C to exit")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        gallery.stop()

if __name__ == "__main__":
    main()
