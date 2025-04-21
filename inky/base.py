"""Inky e-Ink Display Base Class."""
from abc import ABC, abstractmethod

class BaseInky(ABC):
    """Abstract base class for Inky e-Ink Display drivers."""

    # Common color constants
    WHITE = 0
    BLACK = 1
    RED = 2
    YELLOW = 2
    GREEN = 2
    BLUE = 3
    ORANGE = 6
    CLEAN = 7

    @abstractmethod
    def __init__(self, resolution, colour, **kwargs):
        """Initialize an Inky Display.

        :param resolution: (width, height) in pixels
        :param colour: Display color capability
        """
        self.resolution = resolution
        self.width, self.height = resolution
        self.colour = colour

    @abstractmethod
    def set_pixel(self, x, y, v):
        """Set a single pixel.

        :param x: x position on display
        :param y: y position on display
        :param v: colour to set
        """
        pass

    @abstractmethod
    def set_image(self, image, saturation=0.5):
        """Copy an image to the display.

        :param image: PIL image to display
        :param saturation: Saturation for 7-color displays
        """
        pass

    @abstractmethod
    def set_border(self, colour):
        """Set the border colour.

        :param colour: The border colour.
        """
        pass

    @abstractmethod
    def show(self, busy_wait=True):
        """Show buffer on display.

        :param busy_wait: If True, wait for display update to finish before returning.
        """
        pass

    @abstractmethod
    def setup(self):
        """Set up the display and initialize hardware."""
        pass
