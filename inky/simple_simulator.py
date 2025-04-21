"""Simple PIL-based simulator for Inky displays when pygame is not available."""
import time
import numpy as np
from PIL import Image
from .base import BaseInky

class InkySimpleSimulator(BaseInky):
    """Simple PIL-based simulator for Inky displays."""

    def __init__(self, display_type="impressions", colour="multi", **kwargs):
        """Initialize a simple Inky Display Simulator.
        
        :param display_type: Type of display (used to determine resolution)
        :param colour: Display color capability
        """
        # Determine resolution based on display type
        if display_type == "phat":
            resolution = (212, 104)
        elif display_type == "phatssd1608":
            resolution = (250, 122)
        elif display_type == "what" or display_type == "whatssd1683":
            resolution = (400, 300)
        elif display_type == "impressions73":
            resolution = (800, 480)
        else:  # Default to impressions/7colour
            resolution = (600, 448)
            colour = "multi"
        
        super().__init__(resolution, colour, **kwargs)
        
        # Initialize buffer as zeros
        try:
            self.buf = np.zeros((self.height, self.width), dtype=np.uint8)
        except:
            # Fallback if numpy is not available
            self.buf = [[0 for x in range(self.width)] for y in range(self.height)]
        
        self.border_colour = self.WHITE
        self.h_flip = kwargs.get('h_flip', False)
        self.v_flip = kwargs.get('v_flip', False)
        self.rotation = 0
        self.image = None  # Store the last image for show()
        
        # Define color palettes for 7-color displays
        self.DESATURATED_PALETTE = [
            [0, 0, 0],        # Black
            [255, 255, 255],  # White
            [0, 255, 0],      # Green
            [0, 0, 255],      # Blue
            [255, 0, 0],      # Red
            [255, 255, 0],    # Yellow
            [255, 140, 0],    # Orange
            [255, 255, 255]   # Clear
        ]
        
        print(f"Simple Inky Simulator initialized ({self.width}x{self.height}, {self.colour})")
        print("Note: This is a simple simulator that shows images using PIL's show() method.")
        print("Press Ctrl+C to exit.")
    
    def set_pixel(self, x, y, v):
        """Set a single pixel.

        :param x: x position on display
        :param y: y position on display
        :param v: colour to set
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            try:
                self.buf[y][x] = v & 0x07
            except:
                # Handle cases where buffer isn't a numpy array
                if isinstance(self.buf, list):
                    self.buf[y][x] = v & 0x07
    
    def set_image(self, image, saturation=0.5):
        """Copy an image to the display.

        :param image: PIL image to display
        :param saturation: Saturation for 7-color displays
        """
        if not image.size == (self.width, self.height):
            image = image.resize((self.width, self.height))
        
        self.image = image  # Store for later display
        
        # Try to convert the image to the buffer format
        try:
            self.buf = np.array(image, dtype=np.uint8).reshape((self.height, self.width))
        except:
            # If we can't convert to numpy array, just store the image
            pass
    
    def set_border(self, colour):
        """Set the border colour.

        :param colour: The border colour.
        """
        self.border_colour = colour
    
    def setup(self):
        """Set up the display (not needed for simulator)."""
        pass
    
    def show(self, busy_wait=True):
        """Show buffer on display using PIL's show method.

        :param busy_wait: Ignored in simple simulator.
        """
        print("Displaying image...")
        
        # Convert buffer to PIL Image
        if hasattr(self, 'image') and self.image is not None:
            # If set_image was called, use that image
            img = self.image.copy()
        else:
            # Otherwise convert from buffer
            try:
                if isinstance(self.buf, np.ndarray):
                    img = Image.fromarray(self.buf)
                else:
                    # Create a new image and populate from buffer list
                    img = Image.new("P", (self.width, self.height))
                    for y in range(self.height):
                        for x in range(self.width):
                            try:
                                img.putpixel((x, y), self.buf[y][x])
                            except:
                                # Skip any pixels that cause errors
                                pass
            except:
                # If conversion fails, create a blank image as fallback
                img = Image.new("RGB", (self.width, self.height), (255, 255, 255))
                print("Warning: Could not convert buffer to image")
        
        # Apply flips and rotations
        try:
            if self.v_flip:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            
            if self.h_flip:
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
            
            if self.rotation:
                # Handle Image.ROTATE_* constants in different PIL versions
                if hasattr(Image, 'ROTATE_90'):
                    # Older PIL versions
                    rotations = {
                        90: Image.ROTATE_90,
                        180: Image.ROTATE_180,
                        270: Image.ROTATE_270
                    }
                    if self.rotation in rotations:
                        img = img.transpose(rotations[self.rotation])
                else:
                    # Newer PIL versions
                    img = img.rotate(-self.rotation, expand=True)
        except Exception as e:
            print(f"Warning: Error applying transformations: {e}")
        
        # Display the image
        try:
            img.show()
        except Exception as e:
            print(f"Error showing image: {e}")
        
        # Simulate e-ink refresh delay
        time.sleep(1.0)
        print("Display updated.")
    
    def wait_for_window_close(self):
        """Wait until the user closes the PIL window (not implemented)."""
        print("Simple simulator does not support wait_for_window_close.")
        print("Press Ctrl+C to exit.")
    
    def register_button_handler(self, button, handler):
        """Register a handler for button presses (not implemented in simple simulator)."""
        print(f"Button '{button}' registration not supported in simple simulator.")
