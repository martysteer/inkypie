# Cross-Platform Inky Library

This update brings significant enhancements to the Inky library, making it more developer-friendly and cross-platform compatible.

## Key Features

### 1. Seamless Cross-Platform Development

The library now detects whether it's running on Raspberry Pi hardware or another platform and automatically uses the appropriate implementation:

- On Raspberry Pi: Uses the real hardware drivers
- On other platforms: Uses a simulator to visualize e-ink displays

```python
from inky import create_inky, is_raspberry_pi

# Same code works on both Raspberry Pi and other platforms
display = create_inky("impressions")  # 7-color display

if is_raspberry_pi():
    print("Using real hardware")
else:
    print("Using simulator")

# These operations work the same on both platforms
display.set_image(my_image)
display.show()
```

### 2. Enhanced Simulator

The new simulator provides a more accurate representation of e-ink displays:

- Simulates the refresh pattern of e-ink displays
- Supports all Inky display types and color modes
- Handles button input simulation (A, B, C, D) via keyboard
- Realistic rendering of display characteristics

### 3. Development Tools

New debugging and development tools make it easier to work with e-ink displays:

```python
from inky import auto
from inky.debug import InkyDebugger, FastModeEnabler

# Get display instance
inky = auto()

# Attach debugger
debugger = InkyDebugger(inky)
debugger.toggle_grid()  # Show grid overlay
debugger.print_display_info()  # Show detailed display information

# Enable fast mode for development (bypasses e-ink timing)
fast_mode = FastModeEnabler(inky)
fast_mode.enable()  # Speed up refresh for development

# Draw test pattern to see all available colors
debugger.draw_test_pattern()
```

### 4. Configuration Options

You can control the library behavior through environment variables or code:

- `INKY_FORCE_SIMULATION=1` - Forces simulation mode even on Raspberry Pi
- Pass `simulation=True` to `auto()` or `create_inky()` to force simulation

## Getting Started with Cross-Platform Development

### Installation

```bash
pip install inky
```

For simulator capabilities on non-Raspberry Pi platforms:
```bash
pip install pygame  # Recommended for best simulation
```

### Basic Usage

```python
from inky import create_inky

# Create an Inky display (hardware or simulator based on platform)
display = create_inky("phat", "red")  # For red pHAT
# OR
display = create_inky("impressions")  # For 7-color Impression

# Use the display as normal
from PIL import Image, ImageDraw
img = Image.new("P", (display.width, display.height), display.WHITE)
draw = ImageDraw.Draw(img)
draw.rectangle([(0, 0), (display.width - 1, display.height - 1)], outline=display.BLACK)
draw.text((10, 10), "Hello World!", fill=display.BLACK)

display.set_image(img)
display.show()
```

### Examples

Check out the `examples/cross_platform.py` script for a complete example of cross-platform development.

Run it with:
```bash
python examples/cross_platform.py --type impressions
```

### Tips for Cross-Platform Development

1. **Use the factory functions** (`create_inky()` or `auto()`) rather than direct class instantiation for portability.

2. **Test on both platforms** - Your code will work seamlessly on both Raspberry Pi and development machines.

3. **Use environment variables** for quick testing:
   ```bash
   INKY_FORCE_SIMULATION=1 python your_script.py  # Force simulation
   ```

4. **Use debugging tools** - The InkyDebugger class can help identify issues with your display.

5. **Consider screen differences** - The simulator tries to be accurate, but real e-ink displays have unique characteristics.

## For Library Contributors

The updated library architecture follows a clean separation of concerns:

- `base.py` - Abstract base class defining the interface
- `platform.py` - Platform detection utilities
- `factory.py` - Factory functions to create appropriate implementations
- `simulator.py` - Pygame-based simulator implementation
- `simple_simulator.py` - Fallback simulator for when pygame isn't available
- `debug.py` - Development and debugging tools

This makes it easier to maintain and extend the library while ensuring backward compatibility.
