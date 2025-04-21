"""Debug and development tools for Inky displays."""
import time
import threading
import sys
import logging
from PIL import Image, ImageDraw, ImageFont
from .base import BaseInky
from .platform import is_raspberry_pi

# Set up logging
logger = logging.getLogger("inky.debug")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class InkyDebugger:
    """Debugging tools for Inky displays."""
    
    def __init__(self, inky_instance, log_level=logging.INFO):
        """Initialize the debugger with an Inky display instance.
        
        :param inky_instance: Inky display instance to debug
        :param log_level: Logging level (default: INFO)
        """
        if not isinstance(inky_instance, BaseInky):
            raise TypeError("inky_instance must be an Inky display instance")
        
        self.inky = inky_instance
        self.width = inky_instance.width
        self.height = inky_instance.height
        
        # Save original methods
        self.original_show = inky_instance.show
        self.original_set_image = inky_instance.set_image
        
        # Debug flags
        self.show_grid = False
        self.show_coordinates = False
        self.show_timing = True
        self.debug_border = False
        
        # Performance data
        self.refresh_times = []
        self.avg_refresh_time = 0
        
        # Set up logging
        logger.setLevel(log_level)
        
        # Monkey patch the inky methods to add debugging
        inky_instance.show = self._debug_show
        inky_instance.set_image = self._debug_set_image
        
        logger.info(f"Inky debugger attached to {type(inky_instance).__name__} ({self.width}x{self.height})")
    
    def _debug_show(self, busy_wait=True):
        """Debug wrapper for the show method."""
        logger.info("Display update requested")
        
        start_time = time.time()
        self.original_show(busy_wait)
        end_time = time.time()
        
        elapsed = end_time - start_time
        self.refresh_times.append(elapsed)
        
        # Update average
        self.avg_refresh_time = sum(self.refresh_times) / len(self.refresh_times)
        
        logger.info(f"Display updated in {elapsed:.2f}s (avg: {self.avg_refresh_time:.2f}s)")
        return elapsed
    
    def _debug_set_image(self, image, *args, **kwargs):
        """Debug wrapper for the set_image method."""
        logger.info(f"Setting image: {image.width}x{image.height}, mode={image.mode}")
        
        # Add debug overlays if needed
        if self.show_grid or self.show_coordinates:
            # Create a copy of the image to avoid modifying the original
            debug_image = image.copy()
            draw = ImageDraw.Draw(debug_image)
            
            if self.show_grid:
                self._draw_grid(draw)
            
            if self.show_coordinates:
                self._draw_coordinates(draw)
            
            # Pass the modified image to the original method
            return self.original_set_image(debug_image, *args, **kwargs)
        
        # Otherwise, just pass through to the original method
        return self.original_set_image(image, *args, **kwargs)
    
    def _draw_grid(self, draw, spacing=50, color=None):
        """Draw a grid overlay on the image."""
        # Determine color based on display type
        if color is None:
            if hasattr(self.inky, "BLACK"):
                color = self.inky.BLACK
            else:
                color = 0  # Default
        
        # Draw vertical lines
        for x in range(0, self.width, spacing):
            draw.line([(x, 0), (x, self.height - 1)], fill=color, width=1)
        
        # Draw horizontal lines
        for y in range(0, self.height, spacing):
            draw.line([(0, y), (self.width - 1, y)], fill=color, width=1)
    
    def _draw_coordinates(self, draw, spacing=100, color=None, font_size=12):
        """Draw coordinate markers on the image."""
        # Determine color based on display type
        if color is None:
            if hasattr(self.inky, "BLACK"):
                color = self.inky.BLACK
            else:
                color = 0  # Default
        
        # Try to load a font, fall back to default if not available
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
        
        # Draw coordinates at regular intervals
        for x in range(0, self.width, spacing):
            for y in range(0, self.height, spacing):
                label = f"({x},{y})"
                # Check for different versions of PIL with different textbbox methods
                if hasattr(draw, 'textbbox'):
                    draw.text((x + 2, y + 2), label, fill=color, font=font)
                else:
                    # Fall back to older PIL versions
                    draw.text((x + 2, y + 2), label, fill=color, font=font)
    
    def draw_test_pattern(self):
        """Draw a test pattern showing available colors on the display."""
        logger.info("Drawing test pattern")
        
        # Create a new image
        image = Image.new("P", (self.width, self.height), 0)
        draw = ImageDraw.Draw(image)
        
        # Determine colors based on display type
        if hasattr(self.inky, "CLEAN"):
            # 7-color display
            colors = [
                (self.inky.BLACK, "Black"),
                (self.inky.WHITE, "White"),
                (self.inky.GREEN, "Green"),
                (self.inky.BLUE, "Blue"),
                (self.inky.RED, "Red"),
                (self.inky.YELLOW, "Yellow"),
                (self.inky.ORANGE, "Orange"),
                (self.inky.CLEAN, "Clean"),
            ]
        elif hasattr(self.inky, "RED") or hasattr(self.inky, "YELLOW"):
            # Red or yellow display
            colors = [
                (self.inky.BLACK, "Black"),
                (self.inky.WHITE, "White"),
                (self.inky.RED if hasattr(self.inky, "RED") else self.inky.YELLOW, 
                 "Red" if hasattr(self.inky, "RED") else "Yellow"),
            ]
        else:
            # Black and white display
            colors = [
                (self.inky.BLACK, "Black"),
                (self.inky.WHITE, "White"),
            ]
        
        # Calculate the height of each color band
        band_height = self.height // len(colors)
        
        # Draw each color band
        for i, (color_value, color_name) in enumerate(colors):
            y_start = i * band_height
            y_end = (i + 1) * band_height if i < len(colors) - 1 else self.height
            
            # Draw the color rectangle
            draw.rectangle([(0, y_start), (self.width, y_end)], fill=color_value)
            
            # Draw the color name
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
            
            # Use contrasting text color
            text_color = self.inky.WHITE if color_value != self.inky.WHITE else self.inky.BLACK
            
            # Position text in center of band
            try:
                # For newer PIL versions
                if hasattr(draw, 'textbbox'):
                    text_width, text_height = draw.textbbox((0, 0), color_name, font=font)[2:4]
                else:
                    # For older PIL versions
                    text_width, text_height = draw.textsize(color_name, font=font)
            except:
                # Fallback if text measuring fails
                text_width, text_height = len(color_name) * 10, 20
                
            x_text = (self.width - text_width) // 2
            y_text = y_start + (band_height - text_height) // 2
            
            draw.text((x_text, y_text), color_name, fill=text_color, font=font)
        
        # Apply the test pattern
        self.inky.set_image(image)
        self.inky.show()
    
    def toggle_grid(self):
        """Toggle grid overlay."""
        self.show_grid = not self.show_grid
        logger.info(f"Grid overlay {'enabled' if self.show_grid else 'disabled'}")
        return self.show_grid
    
    def toggle_coordinates(self):
        """Toggle coordinate markers."""
        self.show_coordinates = not self.show_coordinates
        logger.info(f"Coordinate markers {'enabled' if self.show_coordinates else 'disabled'}")
        return self.show_coordinates
    
    def toggle_timing(self):
        """Toggle timing information."""
        self.show_timing = not self.show_timing
        logger.info(f"Timing information {'enabled' if self.show_timing else 'disabled'}")
        return self.show_timing
    
    def print_display_info(self):
        """Print detailed information about the display."""
        display_type = type(self.inky).__name__
        
        print("\n=== INKY DISPLAY INFORMATION ===")
        print(f"Display Type: {display_type}")
        print(f"Resolution: {self.width} x {self.height}")
        print(f"Colour Mode: {self.inky.colour}")
        print(f"Platform: {'Raspberry Pi' if is_raspberry_pi() else 'Simulator'}")
        
        # Try to access additional attributes
        try:
            print(f"Rotation: {self.inky.rotation if hasattr(self.inky, 'rotation') else 'Unknown'}")
            print(f"H-Flip: {self.inky.h_flip if hasattr(self.inky, 'h_flip') else 'Unknown'}")
            print(f"V-Flip: {self.inky.v_flip if hasattr(self.inky, 'v_flip') else 'Unknown'}")
        except:
            pass
        
        print("\n=== PERFORMANCE METRICS ===")
        if self.refresh_times:
            print(f"Last Refresh Time: {self.refresh_times[-1]:.2f}s")
            print(f"Average Refresh Time: {self.avg_refresh_time:.2f}s")
            print(f"Fastest Refresh: {min(self.refresh_times):.2f}s")
            print(f"Slowest Refresh: {max(self.refresh_times):.2f}s")
            print(f"Total Refreshes: {len(self.refresh_times)}")
        else:
            print("No refresh data available yet.")
        
        print("\n=== DEBUG SETTINGS ===")
        print(f"Grid Overlay: {'Enabled' if self.show_grid else 'Disabled'}")
        print(f"Coordinate Markers: {'Enabled' if self.show_coordinates else 'Disabled'}")
        print(f"Timing Information: {'Enabled' if self.show_timing else 'Disabled'}")
        print("============================\n")

class FastModeEnabler:
    """Temporarily enables fast mode for e-ink display development."""
    
    def __init__(self, inky_instance):
        """Initialize with an Inky display instance.
        
        :param inky_instance: Inky display instance
        """
        self.inky = inky_instance
        self.original_show = inky_instance.show
        self.original_update = None
        self.enabled = False
        
        # Look for _update method (varies between display types)
        if hasattr(inky_instance, '_update'):
            self.original_update = inky_instance._update
        
        logger.info("Fast mode enabler initialized (not activated)")
    
    def enable(self):
        """Enable fast mode by disabling e-ink timing constraints."""
        if self.enabled:
            logger.info("Fast mode is already enabled")
            return
            
        logger.warning("Enabling FAST MODE - This bypasses e-ink timing for development only")
        logger.warning("Do not use fast mode for extended periods on real hardware!")
        
        # Patch _update method if it exists
        if self.original_update is not None:
            def fast_update(*args, **kwargs):
                if 'busy_wait' in kwargs:
                    kwargs['busy_wait'] = False
                return self.original_update(*args, **kwargs)
            
            self.inky._update = fast_update
        
        # Patch show method
        def fast_show(busy_wait=False):
            return self.original_show(busy_wait=False)
        
        self.inky.show = fast_show
        
        # Patch busy_wait if it exists
        if hasattr(self.inky, '_busy_wait'):
            original_busy_wait = self.inky._busy_wait
            
            def fast_busy_wait(*args, **kwargs):
                # Just return immediately
                return
            
            self.inky._busy_wait = fast_busy_wait
        
        self.enabled = True
        logger.info("Fast mode enabled - refresh delays bypassed")
    
    def disable(self):
        """Disable fast mode, restoring original timing."""
        if not self.enabled:
            logger.info("Fast mode is not enabled")
            return
            
        # Restore original methods
        self.inky.show = self.original_show
        
        if self.original_update is not None:
            self.inky._update = self.original_update
        
        # Restore busy_wait if we patched it
        if hasattr(self.inky, '_busy_wait') and self.inky._busy_wait.__name__ == 'fast_busy_wait':
            delattr(self.inky, '_busy_wait')
        
        self.enabled = False
        logger.info("Fast mode disabled - normal timing restored")
