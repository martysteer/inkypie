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
        
        self.buf = np.zeros((self.height, self.width), dtype=np.uint8)
        self.border_colour = self.WHITE
        self.h_flip = kwargs.get('h_flip', False)
        self.v_flip = kwargs.get('v_flip', False)
        self.rotation = 0
        
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
            self.buf[y][x] = v & 0x07
    
    def set_image(self, image, saturation=0.5):
        """Copy an image to the display.

        :param image: PIL image to display
        :param saturation: Saturation for 7-color displays
        """
        if not image.size == (self.width, self.height):
            image = image.resize((self.width, self.height))
        
        self.image = image  # Store for later display
        self.buf = np.array(image, dtype=np.uint8).reshape((self.height, self.width))
    
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
        if hasattr(self, 'image'):
            # If set_image was called, use that image
            img = self.image
        else:
            # Otherwise convert from buffer
            img = Image.fromarray(self.buf)
        
        # Apply flips and rotations
        if self.v_flip:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        
        if self.h_flip:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        
        if self.rotation:
            if self.rotation == 90:
                img = img.transpose(Image.ROTATE_90)
            elif self.rotation == 180:
                img = img.transpose(Image.ROTATE_180)
            elif self.rotation == 270:
                img = img.transpose(Image.ROTATE_270)
        
        # Display the image
        img.show()
        
        # Simulate e-ink refresh delay
        time.sleep(1.0)
        print("Display updated.")
    
    def wait_for_window_close(self):
        """Wait until the user closes the PIL window (not implemented)."""
        print("Simple simulator does not support wait_for_window_close.")
        print("Press Ctrl+C to exit.")
