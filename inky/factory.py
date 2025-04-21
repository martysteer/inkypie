"""Factory functions for creating appropriate Inky implementations."""
import importlib
import os
import sys
from .platform import should_use_hardware, get_implementation_type

# Dictionary mapping display types to their implementation classes
HARDWARE_DISPLAY_CLASSES = {
    "phat": "inky.phat.InkyPHAT",
    "what": "inky.what.InkyWHAT",
    "phatssd1608": "inky.phat.InkyPHAT_SSD1608",
    "impressions": "inky.inky_uc8159.Inky",
    "7colour": "inky.inky_uc8159.Inky",
    "whatssd1683": "inky.inky_ssd1683.Inky",
    "impressions73": "inky.inky_ac073tc1a.Inky"
}

# Dictionary mapping display types to their simulator classes
SIMULATOR_DISPLAY_CLASSES = {
    "phat": "inky.simulator.InkySimulator",
    "what": "inky.simulator.InkySimulator",
    "phatssd1608": "inky.simulator.InkySimulator",
    "impressions": "inky.simulator.InkySimulator",
    "7colour": "inky.simulator.InkySimulator",
    "whatssd1683": "inky.simulator.InkySimulator",
    "impressions73": "inky.simulator.InkySimulator"
}

# Resolution mappings for simulators
RESOLUTION_MAPPINGS = {
    "phat": (212, 104),
    "what": (400, 300),
    "phatssd1608": (250, 122),
    "impressions": (600, 448),
    "7colour": (600, 448),
    "whatssd1683": (400, 300),
    "impressions73": (800, 480)
}

def dynamic_import(class_path):
    """Dynamically import a class from a string path."""
    module_path, class_name = class_path.rsplit('.', 1)
    
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Failed to import {class_path}: {e}")

def create_hardware_inky(display_type, colour=None, **kwargs):
    """Create a hardware Inky implementation.
    
    :param display_type: Type of Inky display
    :param colour: Colour capability (if applicable)
    :return: Appropriate hardware Inky implementation
    """
    if display_type not in HARDWARE_DISPLAY_CLASSES:
        raise ValueError(f"Unknown display type: {display_type}")
    
    # Import the appropriate class
    class_path = HARDWARE_DISPLAY_CLASSES[display_type]
    try:
        InkyClass = dynamic_import(class_path)
    except ImportError as e:
        print(f"Warning: Could not import hardware class {class_path}: {e}")
        print("Falling back to simulator...")
        return create_simulator_inky(display_type, colour, **kwargs)
    
    # Check if we need to pass the colour parameter
    if display_type in ("impressions", "7colour", "impressions73"):
        # These don't take a colour parameter
        return InkyClass(**kwargs)
    else:
        # These require a colour parameter
        if colour is None:
            raise ValueError(f"Colour must be specified for {display_type}")
        return InkyClass(colour, **kwargs)

def create_simulator_inky(display_type, colour=None, use_pygame=True, **kwargs):
    """Create a simulator Inky implementation.
    
    :param display_type: Type of Inky display to simulate
    :param colour: Colour capability (if applicable)
    :param use_pygame: Whether to use pygame (True) or simple PIL simulator (False)
    :return: Appropriate simulator Inky implementation
    """
    # Set default colour based on display type
    if colour is None:
        if display_type in ("impressions", "7colour", "impressions73"):
            colour = "multi"
        else:
            colour = "black"  # Default
    
    # Get appropriate resolution for this display type
    resolution = kwargs.get('resolution', None) or RESOLUTION_MAPPINGS.get(display_type, (600, 448))
    
    # Try advanced simulator first
    if use_pygame:
        try:
            from .simulator import InkySimulator
            return InkySimulator(resolution=resolution, colour=colour, **kwargs)
        except ImportError as e:
            print(f"Advanced simulator not available: {e}")
            print("Falling back to simple simulator...")
            use_pygame = False
    
    # Fall back to simple simulator
    try:
        from .simple_simulator import InkySimpleSimulator
        return InkySimpleSimulator(display_type=display_type, colour=colour, **kwargs)
    except ImportError as e:
        print(f"Simple simulator not available: {e}")
        raise ImportError("No simulator implementation available. Please check your installation.")

def create_inky(display_type, colour=None, simulation=None, verbose=False, **kwargs):
    """Create appropriate Inky implementation based on platform and settings.
    
    :param display_type: Type of Inky display
    :param colour: Colour capability (if applicable)
    :param simulation: Force simulation mode (True/False), or auto-detect (None)
    :param verbose: Print verbose information
    :return: Appropriate Inky implementation
    """
    # Determine if we should use hardware or simulator
    use_hardware = should_use_hardware()
    
    # Override with simulation parameter if provided
    if simulation is not None:
        use_hardware = not simulation
    
    # Debug info
    if verbose:
        implementation_type = "hardware" if use_hardware else "simulator"
        print(f"Creating {implementation_type} implementation for {display_type} ({colour})")
    
    if use_hardware:
        try:
            return create_hardware_inky(display_type, colour, **kwargs)
        except (ImportError, ValueError) as e:
            if verbose:
                print(f"Warning: Hardware implementation failed ({e}), falling back to simulator")
            return create_simulator_inky(display_type, colour, **kwargs)
    else:
        return create_simulator_inky(display_type, colour, **kwargs)
