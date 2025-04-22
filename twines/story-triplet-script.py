#!/usr/bin/env python3
"""
Inky Story Builder - Create short stories by selecting word triplets
For Inky e-ink displays with button controls.

Requires: Inky library, fonts
"""
import argparse
import sys
import time
import platform
import json
from PIL import Image, ImageDraw, ImageFont

# Check if we're on macOS or another non-Pi system
IS_SIMULATION = platform.system() != "Linux" or not platform.machine().startswith("arm")

# Only try to import hardware-dependent libraries if not in simulation mode
if not IS_SIMULATION:
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
else:
    BUTTON_SUPPORT = False
    print("Running in simulation mode - hardware features disabled")

# Button pins (Raspberry Pi GPIO)
BUTTONS = [5, 6, 16, 24]  # A, B, C, D buttons
LABELS = ["A", "B", "C", "D"]

# Story data (themes, characters, settings, etc.)
STORY_DATA = {
  "theme_specific": {
    "cinematic_noir": {
      "Character": ["Private Eye", "Silent Dancer", "Street Hustler", "Jazz Singer", "Detective"],
      "Setting": ["Foggy Alley", "Neon Bar", "Rain-Slicked Street", "Motel Room", "Rooftop Edge"],
      "Clue_Moment": ["Whispered Name", "Dropped Lighter", "Glint of Steel", "Phone Off Hook", "Final Glance"]
    },
    "romantic_dreamlike": {
      "Persona": ["Stargazer", "Writer", "Painter", "Lover", "Stranger"],
      "Scene": ["Flower Field", "Rainy Window", "Sunset Dock", "Old Café", "Paris Balcony"],
      "Emotion": ["Hopeful Longing", "Gentle Ache", "Fleeting Joy", "Blooming Warmth", "Timeless Yearning"]
    },
    "moody_introspective": {
      "Figure": ["Drifter", "Old Soul", "Outsider", "Thinker", "Watcher"],
      "Space": ["Empty Lot", "Dusty Library", "Forest Path", "Overpass", "Cracked Sidewalk"],
      "Mood": ["Disconnection", "Quiet Melancholy", "Fading Light", "Bitter Calm", "Still Reflection"]
    },
    "retro_nostalgic": {
      "Icon": ["Milkman", "Mod Girl", "Greaser", "Film Star", "War Bride"],
      "Era_Location": ["1950s Suburb", "60s Diner", "Drive-In", "Red Carpet", "Train Station"],
      "Item_Trigger": ["Tin Lunchbox", "Roller Skates", "Jukebox Tune", "Pocket Camera", "Love Letter"]
    },
    "gritty_real": {
      "Human_Detail": ["Torn Hoodie", "Bruised Knuckles", "Tight Grip", "Cracked Smile", "Bent Posture"],
      "Urban_Texture": ["Brick Wall", "Chain-Link Fence", "Scuffed Concrete", "Rusted Sign", "Flickering Lamp"],
      "Incident": ["Bike Crash", "Missed Shot", "Siren Echo", "Lost Wallet", "Screamed Name"]
    }
  },
  "vignettes": {
    "cinematic_noir": {
      "Private Eye|Motel Room|Dropped Lighter": "The lighter clinked on tile, still warm. He didn't need the matchbook clue—it was her scent on the pillow that burned. The motel room whispered old lies with fresh breath. Cigarette smoke hung like a question mark. Outside, the case kept unfolding, but she'd already rewritten the ending.",
      "Detective|Foggy Alley|Glint of Steel": "The fog twisted around her ankles as she moved deeper into the alley. A distant flash—metal catching light. She froze, hand on her holster. Twenty years on the force taught her that steel in darkness rarely offered second chances."
    },
    "romantic_dreamlike": {
      "Painter|Sunset Dock|Fleeting Joy": "She painted until the sun dipped low, each brushstroke pulling memories from the water's edge. He never returned, but the glow on the dock held his shape. The canvas dried with her smile—thin, unfinished. The joy, like light, touched everything briefly before fading into evening."
    },
    "retro_nostalgic": {
      "War Bride|Train Station|Love Letter": "She stood where he'd promised, the letter folded tight in her glove. Steam curled around her heels as the train departed again—empty. Each year, same place. She wasn't waiting for him anymore, not really. Only for the sound of wheels and the echo of paper words."
    },
    "moody_introspective": {
      "Drifter|Forest Path|Fading Light": "He walked paths that never stayed the same. Each fork led deeper into the hush of trees, dusk dimming all directions. The light thinned like old film reels, catching on branches, slipping through. He never looked back; the forest, like his past, never gave him the option."
    },
    "gritty_real": {
      "Torn Hoodie|Brick Wall|Siren Echo": "He sprinted past the mural, shoes hitting pavement like a drumline. Sirens tangled with city echoes, bouncing between alleys and broken bricks. His hoodie flapped, threadbare and real. Behind him, names were being shouted. Ahead, a single alley light flickered, no promise of safety—just another turn in the grid."
    }
  }
}

class InkyMock:
    """Simple mock Inky display for development/simulation."""
    def __init__(self, width=600, height=448):
        self.width = width
        self.height = height
        self.WHITE = 1
        self.BLACK = 0
        self.image = None
        print(f"Created mock Inky display ({width}x{height})")
    
    def set_border(self, color):
        pass
    
    def set_image(self, image, saturation=0.5):
        self.image = image
        # Display the image using PIL's show method when not on an actual device
        self.image.show()
    
    def show(self):
        print("Display updated (simulation)")

class StoryBuilder:
    """Main class for the Inky Story Builder"""
    
    def __init__(self, inky_display, theme="cinematic_noir", verbose=False, simulation=False):
        """Initialize the story builder with display and theme"""
        self.inky_display = inky_display
        self.verbose = verbose
        self.simulation = simulation
        self.current_theme = theme
        self.mode = 0  # 0=theme select, 1,2,3=category select, 4=story view
        self.running = True
        self.button_thread = None
        self.last_button_time = 0
        self.debounce_time = 0.5  # seconds
        
        # Set up theme data
        self.themes = list(STORY_DATA["theme_specific"].keys())
        self.theme_index = self.themes.index(theme) if theme in self.themes else 0
        
        # Initialize selections
        self.current_categories = self.get_categories(self.themes[self.theme_index])
        self.category_indexes = [0, 0, 0]
        
        # Set up buttons if available and not in simulation mode
        if BUTTON_SUPPORT and not simulation:
            self.setup_buttons()
        
        # Prepare fonts - try to load them, fall back to default if not available
        try:
            self.title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
            self.normal_font = ImageFont.truetype("DejaVuSans.ttf", 16)
            self.small_font = ImageFont.truetype("DejaVuSans.ttf", 12)
        except IOError:
            # Fall back to default PIL font if custom fonts not available
            self.title_font = ImageFont.load_default()
            self.normal_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()
    
    def setup_buttons(self):
        """Set up button handling"""
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
            self.request = self.chip.request_lines(consumer="inky-story-builder", config=line_config)
            
            # Start button handling thread
            import threading
            self.button_thread = threading.Thread(target=self.button_handler, daemon=True)
            self.button_thread.start()
            
            if self.verbose:
                print("Button controls enabled:")
                print("  A: Select / Confirm")
                print("  B: Next option")
                print("  C: Previous option")
                print("  D: Back / Mode toggle")
                
        except Exception as e:
            print(f"Error setting up buttons: {e}")
            print("Button controls disabled")
    
    def button_handler(self):
        """Handle button presses in a separate thread"""
        while self.running:
            try:
                for event in self.request.read_edge_events():
                    self.handle_button_press(event)
            except Exception as e:
                if self.verbose:
                    print(f"Button error: {e}")
                time.sleep(0.1)
    
    def handle_button_press(self, event):
        """Process button press events"""
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
            if label == "A":  # Select / Confirm
                self.button_select()
            elif label == "B":  # Next option
                self.button_next()
            elif label == "C":  # Previous option
                self.button_prev()
            elif label == "D":  # Back / Mode
                self.button_back()
                
        except Exception as e:
            if self.verbose:
                print(f"Error handling button: {e}")
    
    def get_categories(self, theme):
        """Get the categories for the current theme"""
        if theme in STORY_DATA["theme_specific"]:
            return list(STORY_DATA["theme_specific"][theme].keys())
        return []

    def get_options(self, theme, category):
        """Get the options for a theme and category"""
        if theme in STORY_DATA["theme_specific"] and category in STORY_DATA["theme_specific"][theme]:
            return STORY_DATA["theme_specific"][theme][category]
        return []
    
    def button_select(self):
        """Action for select button (A)"""
        if self.mode == 0:
            # Selected a theme, move to first category
            self.current_theme = self.themes[self.theme_index]
            self.current_categories = self.get_categories(self.current_theme)
            self.category_indexes = [0, 0, 0]
            self.mode = 1
        elif self.mode >= 1 and self.mode <= 3:
            # Selected a category option, move to next category or story
            self.mode += 1
        elif self.mode == 4:
            # In story view mode, go back to first category
            self.mode = 1
        self.update_display()
    
    def button_next(self):
        """Action for next button (B)"""
        if self.mode == 0:
            # Cycle through themes
            self.theme_index = (self.theme_index + 1) % len(self.themes)
        elif self.mode >= 1 and self.mode <= 3:
            # Cycle through category options
            category_idx = self.mode - 1
            options = self.get_options(self.current_theme, self.current_categories[category_idx])
            self.category_indexes[category_idx] = (self.category_indexes[category_idx] + 1) % len(options)
        self.update_display()
    
    def button_prev(self):
        """Action for previous button (C)"""
        if self.mode == 0:
            # Cycle through themes backwards
            self.theme_index = (self.theme_index - 1) % len(self.themes)
        elif self.mode >= 1 and self.mode <= 3:
            # Cycle through category options backwards
            category_idx = self.mode - 1
            options = self.get_options(self.current_theme, self.current_categories[category_idx])
            self.category_indexes[category_idx] = (self.category_indexes[category_idx] - 1) % len(options)
        self.update_display()
    
    def button_back(self):
        """Action for back/mode button (D)"""
        if self.mode > 0:
            # Go back to previous mode or theme selection
            self.mode -= 1
        else:
            # Toggle between theme selection and category selection
            self.mode = 0
        self.update_display()
    
    def get_current_triplet(self):
        """Get the current triplet of selected words"""
        triplet = []
        for i in range(3):
            category = self.current_categories[i]
            options = self.get_options(self.current_theme, category)
            if options:
                triplet.append(options[self.category_indexes[i]])
        return triplet
    
    def get_vignette(self, triplet):
        """Get a vignette for the current triplet"""
        if len(triplet) < 3:
            return "Make selections to create your story..."
            
        # Try to find a matching vignette
        key = "|".join(triplet)
        if self.current_theme in STORY_DATA["vignettes"] and key in STORY_DATA["vignettes"][self.current_theme]:
            return STORY_DATA["vignettes"][self.current_theme][key]
        
        # Generate a simple fallback vignette
        return f"The {triplet[0]} waited in the {triplet[1]}, anticipating a {triplet[2]}. What happens next is for you to imagine..."
    
    def update_display(self):
        """Update the e-ink display with current UI state"""
        # Create a new image with the display dimensions
        img = Image.new("P", (self.inky_display.width, self.inky_display.height), self.inky_display.WHITE)
        draw = ImageDraw.Draw(img)
        
        # Define positions and sizes
        padding = 10
        title_height = 30
        option_height = 30
        preview_height = 15
        
        # Draw title
        theme_name = self.themes[self.theme_index].replace("_", " ").title()
        if self.mode == 0:
            title = f"Select Theme: {theme_name}"
            draw.rectangle((0, 0, self.inky_display.width, title_height), 
                          fill=self.inky_display.BLACK)
            draw.text((padding, padding/2), title, self.inky_display.WHITE, font=self.title_font)
        else:
            title = f"Theme: {theme_name}"
            draw.rectangle((0, 0, self.inky_display.width, title_height), 
                          fill=self.inky_display.BLACK)
            draw.text((padding, padding/2), title, self.inky_display.WHITE, font=self.title_font)
        
        # Show theme selection
        if self.mode == 0:
            y = title_height + padding
            # Show next/prev theme options
            prev_theme = self.themes[(self.theme_index - 1) % len(self.themes)].replace("_", " ").title()
            next_theme = self.themes[(self.theme_index + 1) % len(self.themes)].replace("_", " ").title()
            
            draw.text((padding, y), "Prev (C): " + prev_theme, self.inky_display.BLACK, font=self.small_font)
            y += preview_height
            draw.text((padding, y), "Next (B): " + next_theme, self.inky_display.BLACK, font=self.small_font)
            y += preview_height + padding
            
            draw.text((padding, y), "Press A to select theme", self.inky_display.BLACK, font=self.normal_font)
            return self.display_image(img)
        
        # Draw category selections
        triplet = []
        for i in range(3):
            y = title_height + (i * (option_height + preview_height + padding)) + padding
            
            # Get category and options
            category = self.current_categories[i]
            options = self.get_options(self.current_theme, category)
            
            # Format category name
            category_name = category.replace("_", " ")
            
            # Check if this category is active
            is_active = (self.mode == i + 1)
            
            # Draw category label and selected option
            if is_active:
                # Draw active category with highlight
                draw.rectangle((0, y, self.inky_display.width, y + option_height), 
                              fill=self.inky_display.BLACK)
                draw.text((padding, y + 5), f"{category_name}:", 
                         self.inky_display.WHITE, font=self.normal_font)
                
                selected_option = options[self.category_indexes[i]]
                draw.text((padding + 100, y + 5), selected_option, 
                         self.inky_display.WHITE, font=self.normal_font)
                
                # Show preview options when active
                prev_idx = (self.category_indexes[i] - 1) % len(options)
                next_idx = (self.category_indexes[i] + 1) % len(options)
                
                preview_y = y + option_height
                draw.text((padding, preview_y), f"← {options[prev_idx]} | {options[next_idx]} →", 
                         self.inky_display.BLACK, font=self.small_font)
            else:
                # Draw inactive category
                draw.text((padding, y + 5), f"{category_name}:", 
                         self.inky_display.BLACK, font=self.normal_font)
                
                if i < len(self.category_indexes) and self.category_indexes[i] < len(options):
                    selected_option = options[self.category_indexes[i]]
                    triplet.append(selected_option)
                    draw.text((padding + 100, y + 5), selected_option, 
                             self.inky_display.BLACK, font=self.normal_font)
        
        # Draw story in story view mode
        if self.mode == 4:
            vignette = self.get_vignette(triplet)
            
            # Calculate position for story text
            story_y = title_height + (3 * (option_height + preview_height + padding)) + padding
            
            # Draw a box for the story
            draw.rectangle((padding, story_y, self.inky_display.width - padding, 
                           self.inky_display.height - padding), 
                          outline=self.inky_display.BLACK)
            
            # Word wrap the story text to fit the display width
            wrapped_text = self.wrap_text(vignette, self.inky_display.width - (padding * 3), self.small_font)
            
            # Draw the story text
            draw.multiline_text((padding * 2, story_y + padding), wrapped_text, 
                              self.inky_display.BLACK, font=self.small_font)
        
        # Draw button guide at the bottom
        button_y = self.inky_display.height - 20
        if self.mode < 4:
            button_text = "A: Select    B: Next    C: Prev    D: Back"
        else:
            button_text = "A: Edit    D: Back to Theme"
        
        draw.text((padding, button_y), button_text, self.inky_display.BLACK, font=self.small_font)
        
        # Display the image
        self.display_image(img)
    
    def wrap_text(self, text, width, font):
        """Wrap text to fit within a given width"""
        lines = []
        for paragraph in text.split('\n'):
            words = paragraph.split()
            current_line = []
            current_width = 0
            
            for word in words:
                word_width = font.getlength(word + " ")
                if current_width + word_width <= width:
                    current_line.append(word)
                    current_width += word_width
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_width = word_width
            
            if current_line:
                lines.append(" ".join(current_line))
        
        return "\n".join(lines)
    
    def display_image(self, img):
        """Display an image on the e-ink display"""
        self.inky_display.set_image(img)
        self.inky_display.show()
    
    def run(self):
        """Main run loop for the story builder"""
        self.update_display()
        
        # If in simulation mode, handle keyboard input
        if self.simulation:
            print("\nSimulation keyboard controls:")
            print("  a: Select / Confirm")
            print("  b: Next option")
            print("  c: Previous option")
            print("  d: Back / Mode")
            print("  q: Quit")
            
            try:
                while self.running:
                    key = input("Press a key (a/b/c/d/q): ").lower()
                    if key == 'a':
                        self.button_select()
                    elif key == 'b':
                        self.button_next()
                    elif key == 'c':
                        self.button_prev()
                    elif key == 'd':
                        self.button_back()
                    elif key == 'q':
                        self.running = False
            except KeyboardInterrupt:
                print("\nExiting...")
        else:
            try:
                # In hardware mode, just keep the main thread alive
                # The button_handler thread will process button presses
                while self.running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\nExiting...")
    
    def stop(self):
        """Clean up resources"""
        self.running = False
        if self.button_thread:
            self.button_thread.join(timeout=1.0)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Inky Story Builder')
    parser.add_argument('--theme', '-t', type=str, default='cinematic_noir',
                        choices=list(STORY_DATA["theme_specific"].keys()),
                        help='Initial theme to use')
    parser.add_argument('--simulation', '-s', action='store_true',
                        help='Run in simulation mode (no hardware)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    args = parser.parse_args()
    
    # Initialize the Inky display
    try:
        if args.simulation or IS_SIMULATION:
            # Use a mock display in simulation mode
            inky_display = InkyMock()
            args.simulation = True
        else:
            # Use actual hardware
            inky_display = auto()
            inky_display.set_border(inky_display.WHITE)
    except Exception as e:
        print(f"Error initializing display: {e}")
        print("Try running with --simulation to test without hardware")
        sys.exit(1)
    
    # Create and run the story builder
    story_builder = StoryBuilder(
        inky_display=inky_display,
        theme=args.theme,
        verbose=args.verbose,
        simulation=args.simulation
    )
    
    try:
        story_builder.run()
    finally:
        story_builder.stop()

if __name__ == "__main__":
    main()
