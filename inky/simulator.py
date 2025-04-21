"""Pygame-based simulator for Inky displays."""
import threading
import time
import numpy as np
from PIL import Image
from .base import BaseInky

try:
    import pygame
except ImportError:
    raise ImportError("Simulator requires pygame. Install with: pip install pygame")

class InkySimulator(BaseInky):
    """Pygame-based simulator for Inky displays."""

    def __init__(self, resolution=(600, 448), colour="multi", **kwargs):
        """Initialize an Inky Display Simulator.

        :param resolution: (width, height) in pixels, default: (600, 448)
        :param colour: Display color capability ("multi", "red", "black", "yellow")
        """
        super().__init__(resolution, colour)
        
        self.buf = np.zeros((self.height, self.width), dtype=np.uint8)
        self.border_colour = self.WHITE
        self.pygame_initialized = False
        self.screen = None
        self.h_flip = kwargs.get('h_flip', False)
        self.v_flip = kwargs.get('v_flip', False)
        self.rotation = 0
        self._running = True
        self._update_requested = False
        self._update_complete = threading.Event()
        self._refresh_fps = 2  # Slow refresh to simulate e-ink
        self._last_frame = None
        
        # Define color palettes
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
        
        self.SATURATED_PALETTE = [
            [57, 48, 57],      # Black
            [255, 255, 255],   # White
            [58, 91, 70],      # Green
            [61, 59, 94],      # Blue
            [156, 72, 75],     # Red
            [208, 190, 71],    # Yellow
            [177, 106, 73],    # Orange
            [255, 255, 255]    # Clear
        ]
        
        # Start the display thread
        self._display_thread = threading.Thread(target=self._display_loop)
        self._display_thread.daemon = True
        self._display_thread.start()
        
        # Define key mappings for button simulation
        self.key_mappings = {
            pygame.K_a: 'A',  # A button
            pygame.K_b: 'B',  # B button
            pygame.K_c: 'C',  # C button
            pygame.K_d: 'D',  # D button
        }
        
        # Button callback handlers
        self.button_handlers = {}
    
    def _palette_blend(self, saturation, dtype="uint8"):
        """Blend between saturated and desaturated palettes."""
        saturation = float(saturation)
        palette = []
        for i in range(7):
            rs, gs, bs = [c * saturation for c in self.SATURATED_PALETTE[i]]
            rd, gd, bd = [c * (1.0 - saturation) for c in self.DESATURATED_PALETTE[i]]
            if dtype == "uint8":
                palette += [int(rs + rd), int(gs + gd), int(bs + bd)]
            if dtype == "uint24":
                palette += [(int(rs + rd) << 16) | (int(gs + gd) << 8) | int(bs + bd)]
        if dtype == "uint8":
            palette += [255, 255, 255]
        if dtype == "uint24":
            palette += [0xFFFFFF]
        return palette
    
    def _display_loop(self):
        """Main display loop for simulator."""
        while self._running:
            if not self.pygame_initialized:
                self._init_pygame()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in self.key_mappings:
                        button = self.key_mappings[event.key]
                        if button in self.button_handlers:
                            for handler in self.button_handlers[button]:
                                handler(button)
            
            # Update display if requested
            if self._update_requested:
                self._update_display()
                self._update_requested = False
                self._update_complete.set()
            
            time.sleep(1.0 / 30)  # 30 FPS UI
    
    def _init_pygame(self):
        """Initialize pygame display."""
        pygame.init()
        pygame.display.set_caption(f"Inky Simulator - {self.width}x{self.height} - {self.colour}")
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.pygame_initialized = True
    
    def _update_display(self):
        """Update the pygame display with current buffer."""
        if not self.pygame_initialized:
            return
        
        # Create PIL image from buffer
        region = self.buf.copy()
        
        if self.v_flip:
            region = np.fliplr(region)
        
        if self.h_flip:
            region = np.flipud(region)
        
        if self.rotation:
            region = np.rot90(region, self.rotation // 90)
        
        # Create PIL image with palette
        img = Image.fromarray(region.astype(np.uint8))
        
        # Apply palette based on color mode
        if self.colour == "multi":
            palette = self._palette_blend(0.5)
            palette_img = Image.new("P", (1, 1))
            palette_img.putpalette(palette + [0, 0, 0] * 248)  # Fill remaining palette
            img = img.convert("RGB", palette=palette_img.getpalette())
        else:
            # For red/black/yellow displays
            if self.colour == "red":
                palette = [255, 255, 255, 0, 0, 0, 255, 0, 0]
            elif self.colour == "yellow":
                palette = [255, 255, 255, 0, 0, 0, 255, 255, 0]
            else:  # black
                palette = [255, 255, 255, 0, 0, 0]
            
            palette_img = Image.new("P", (1, 1))
            palette_img.putpalette(palette + [0, 0, 0] * 252)  # Fill remaining palette
            img = img.convert("P", palette=palette_img)
        
        # Simulate e-ink refresh effect
        if self._last_frame is not None:
            # First flash to white
            self.screen.fill((255, 255, 255))
            pygame.display.flip()
            time.sleep(0.2)
            
            # Then flash to black
            self.screen.fill((0, 0, 0))
            pygame.display.flip()
            time.sleep(0.2)
        
        # Convert to pygame surface and display
        mode = img.mode
        size = img.size
        data = img.tobytes()
        
        # Handle different image modes
        if mode == "P":
            # Convert to RGB for pygame
            img = img.convert("RGB")
            mode = img.mode
            data = img.tobytes()
            
        surface = pygame.image.fromstring(data, size, mode)
        self.screen.blit(surface, (0, 0))
        pygame.display.flip()
        
        self._last_frame = region
    
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
        
        if not image.mode == "P":
            if self.colour == "multi":
                # For 7-color displays
                palette = self._palette_blend(saturation)
                # Image size doesn't matter since it's just the palette we're using
                palette_image = Image.new("P", (1, 1))
                # Set our 7 colour palette (+ clear) and zero out the other 247 colours
                palette_image.putpalette(palette + [0, 0, 0] * 248)
                # Force source image data to be loaded for `.im` to work
                image.load()
                image = image.convert("P", palette=palette_image.palette)
            else:
                # For red/black/yellow displays
                palette_image = Image.new("P", (1, 1))
                r, g, b = 0, 0, 0
                if self.colour == "red":
                    r = 255
                if self.colour == "yellow":
                    r = g = 255
                palette_image.putpalette([255, 255, 255, 0, 0, 0, r, g, b] + [0, 0, 0] * 252)
                image.load()
                image = image.convert("P", palette=palette_image.palette)
        
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
        """Show buffer on display.

        :param busy_wait: If True, wait for display update to finish before returning.
        """
        self._update_requested = True
        if busy_wait:
            self._update_complete.clear()
            self._update_complete.wait()
    
    def wait_for_window_close(self):
        """Wait until the pygame window has closed."""
        if self.pygame_initialized:
            while self._running:
                time.sleep(0.1)
        self._running = False
    
    def register_button_handler(self, button, handler):
        """Register a handler for button presses.

        :param button: Button identifier (A, B, C, D)
        :param handler: Callback function that takes button as argument
        """
        if button not in self.button_handlers:
            self.button_handlers[button] = []
        self.button_handlers[button].append(handler)
