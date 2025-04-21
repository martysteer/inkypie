#!/usr/bin/env python3
"""
Cross-platform Inky example.
This script demonstrates using the new factory pattern to work seamlessly
across Raspberry Pi hardware and other platforms with simulator.
"""
import os
import sys
# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import argparse
from PIL import Image, ImageDraw, ImageFont

# Import from inky using the new factory pattern
from inky import is_raspberry_pi, create_inky, auto
from inky.debug import InkyDebugger, FastModeEnabler

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Cross-platform Inky example")
    parser.add_argument("--type", "-t", choices=["phat", "what", "impressions", "7colour", "auto"], 
                       default="auto", help="Inky display type")
    parser.add_argument("--color", "-c", choices=["black", "red", "yellow", "multi"], 
                       default=None, help="Display color (if applicable)")
    parser.add_argument("--simulate", "-s", action="store_true", 
                       help="Force simulation mode even on Raspberry Pi")
    parser.add_argument("--grid", "-g", action="store_true", 
                       help="Show debug grid overlay")
    parser.add_argument("--fast", "-f", action="store_true", 
                       help="Enable fast mode (bypass e-ink timing)")
    parser.add_argument("--test-pattern", action="store_true", 
                       help="Display test pattern showing available colors")
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    
    # Check if we're on a Raspberry Pi
    if is_raspberry_pi():
        print("Running on Raspberry Pi hardware")
    else:
        print("Running on non-Raspberry Pi platform, using simulator")
        # Force simulation mode on non-Pi platforms
        args.simulate = True
    
    # Get display instance
    if args.type == "auto":
        print("Auto-detecting display...")
        inky = auto(verbose=True, simulation=args.simulate)
    else:
        print(f"Creating {args.type} display...")
        inky = create_inky(args.type, args.color, simulation=args.simulate)
    
    # Attach debugger
    debugger = InkyDebugger(inky)
    if args.grid:
        debugger.toggle_grid()
    
    # Enable fast mode if requested
    if args.fast:
        print("Warning: Fast mode enabled - bypassing e-ink timing constraints")
        fast_mode = FastModeEnabler(inky)
        fast_mode.enable()
    
    # Display test pattern if requested
    if args.test_pattern:
        print("Displaying test pattern...")
        debugger.draw_test_pattern()
        return
    
    # Display information about the display
    debugger.print_display_info()
    
    # Create a simple image to display
    img = Image.new("P", (inky.width, inky.height), inky.WHITE)
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, use default if not available
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw a border
    draw.rectangle([(0, 0), (inky.width - 1, inky.height - 1)], outline=inky.BLACK)
    
    # Draw platform information
    platform_text = "Raspberry Pi Hardware" if is_raspberry_pi() and not args.simulate else "Simulator"
    text_width, text_height = draw.textbbox((0, 0), platform_text, font=font)[2:4]
    x = (inky.width - text_width) // 2
    draw.text((x, 20), platform_text, fill=inky.BLACK, font=font)
    
    # Draw display information
    display_text = f"{inky.width}x{inky.height} {inky.colour}"
    text_width, text_height = draw.textbbox((0, 0), display_text, font=font)[2:4]
    x = (inky.width - text_width) // 2
    draw.text((x, 60), display_text, fill=inky.BLACK, font=font)
    
    # Draw time
    time_text = time.strftime("%H:%M:%S")
    text_width, text_height = draw.textbbox((0, 0), time_text, font=font)[2:4]
    x = (inky.width - text_width) // 2
    draw.text((x, 100), time_text, fill=inky.BLACK, font=font)
    
    # Draw some shapes to demonstrate colors
    colors = [inky.BLACK]
    
    # Add colors based on display type
    if hasattr(inky, "RED"):
        colors.append(inky.RED)
    elif hasattr(inky, "YELLOW"):
        colors.append(inky.YELLOW)
    
    if hasattr(inky, "GREEN"):
        colors.extend([inky.GREEN, inky.BLUE, inky.ORANGE])
    
    # Draw circles with available colors
    radius = 30
    spacing = radius * 3
    start_x = (inky.width - (len(colors) * spacing - spacing // 2)) // 2
    
    for i, color in enumerate(colors):
        center_x = start_x + i * spacing
        center_y = inky.height - 80
        draw.ellipse(
            [(center_x - radius, center_y - radius), 
             (center_x + radius, center_y + radius)], 
            fill=color
        )
    
    # Set the image and display it
    print("Updating display...")
    inky.set_image(img)
    inky.show()
    
    print("Done!")

if __name__ == "__main__":
    main()
