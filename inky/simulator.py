"""Pygame-based simulator for Inky displays."""
import threading
import time
import sys
import numpy as np
from PIL import Image
from .base import BaseInky

# Try to import pygame, but don't fail if it's not available
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not available. Using simple simulator instead.")
    from .simple_simulator import InkySimpleSimulator

class InkySimulator(BaseInky):
    """Pygame-based simulator for Inky displays."""

    def __init__(self, resolution=(600, 448), colour="multi", **kwargs):
        """Initialize an Inky Display Simulator.

        :param resolution: (width, height) in pixels, default: (600, 448)
        :param colour: Display color capability ("multi", "red", "black", "yellow")
        """
        super().__init__(resolution, colour)
        
        # If pygame is not available, fall back to simple simulator
        if not PYGAME_AVAILABLE:
            print("Falling back to simple simulator...")
            self._simple_simulator = InkySimpleSimulator(
                resolution=resolution, 
                colour=colour, 
                **kwargs
            )
            return
        
        try:
            self.buf = np.zeros((self.height, self.width), dtype=np.uint8)
        except:
            # Fallback if numpy is not available
            self.buf = [[0 for x in range(self.width)] for y in range(self.height)]
            
        self.border_colour = self.WHITE
        self.h_flip = kwargs.get('h_flip', False)
        self.v_flip = kwargs.get('v_flip', False)
        self.rotation = 0
        self._running = True
        self._update_requested = False
        self._update_complete = threading.Event()
        self._refresh_fps = 2  # Slow refresh to simulate e-ink
        self._last_frame = None
        self.pygame_initialized = False
        self.screen = None
        
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
        # Exit if pygame not available
        if not PYGAME_AVAILABLE:
            return
            
        try:
            while self._running:
                if not self.pygame_initialized:
                    try:
                        self._init_pygame()
                    except Exception as e:
                        print(f"Error initializing pygame: {e}")
                        time.sleep(1.0)
                        continue
                
                # Handle events
                try:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self._running = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key in self.key_mappings:
                                button = self.key_mappings[event.key]
                                if button in self.button_handlers:
                                    for handler in self.button_handlers[button]:
                                        handler(button)
                except Exception as e:
                    print(f"Error handling pygame events: {e}")
                
                # Update display if requested
                if self._update_requested:
                    try:
                        self._update_display()
                        self._update_requested = False
                        self._update_complete.set()
                    except Exception as e:
                        print(f"Error updating display: {e}")
                
                time.sleep(1.0 / 30)  # 30 FPS UI
        except Exception as e:
            print(f"Display loop error: {e}")
    
    def _init_pygame(self):
        """Initialize pygame display."""
        if not PYGAME_AVAILABLE:
            return
            
        pygame.init()
        pygame.display.set_caption(f"Inky Simulator - {self.width}x{self.height} - {self.colour}")
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.pygame_initialized = True
    
    def _update_display(self):
        """Update the pygame display with current buffer."""
        if not PYGAME_AVAILABLE or not self.pygame_initialized:
            return
        
        try:
            # Create PIL image from buffer
            region = self.buf.copy() if isinstance(self.buf, np.ndarray) else np.array(self.buf)
            
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
        except Exception as e:
            print(f"Error in _update_display: {e}")
    
    # Delegate to simple simulator if pygame not available
    def _check_pygame(self, method_name):
        """Check if pygame is available, otherwise delegate to simple simulator."""
        if not PYGAME_AVAILABLE and hasattr(self, '_simple_simulator'):
            method = getattr(self._simple_simulator, method_name)
            return method
        return None
        
    def set_pixel(self, x, y, v):
        """Set a single pixel.

        :param x: x position on display
        :param y: y position on display
        :param v: colour to set
        """
        delegate = self._check_pygame('set_pixel')
        if delegate:
            return delegate(x, y, v)
            
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
        delegate = self._check_pygame('set_image')
        if delegate:
            return delegate(image, saturation)
            
        if not image.size == (self.width, self.height):
            image = image.resize((self.width, self.height))
        
        try:
            self.buf = np.array(image, dtype=np.uint8).reshape((self.height, self.width))
        except:
            # Store image for later reference if numpy conversion fails
            self.image = image
    
    def set_border(self, colour):
        """Set the border colour.

        :param colour: The border colour.
        """
        delegate = self._check_pygame('set_border')
        if delegate:
            return delegate(colour)
            
        self.border_colour = colour
    
    def setup(self):
        """Set up the display (not needed for simulator)."""
        delegate = self._check_pygame('setup')
        if delegate:
            return delegate()
    
    def show(self, busy_wait=True):
        """Show buffer on display.

        :param busy_wait: If True, wait for display update to finish before returning.
        """
        delegate = self._check_pygame('show')
        if delegate:
            return delegate(busy_wait)
            
        self._update_requested = True
        if busy_wait:
            self._update_complete.clear()
            self._update_complete.wait()
    
    def wait_for_window_close(self):
        """Wait until the pygame window has closed."""
        delegate = self._check_pygame('wait_for_window_close')
        if delegate:
            return delegate()
            
        if self.pygame_initialized:
            while self._running:
                time.sleep(0.1)
        self._running = False
    
    def register_button_handler(self, button, handler):
        """Register a handler for button presses.

        :param button: Button identifier (A, B, C, D)
        :param handler: Callback function that takes button as argument
        """
        delegate = self._check_pygame('register_button_handler')
        if delegate:
            return delegate(button, handler)
            
        if button not in self.button_handlers:
            self.button_handlers[button] = []
        self.button_handlers[button].append(handler)
