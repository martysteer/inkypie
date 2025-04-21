"""Automatic Inky setup from i2c EEPROM."""
import argparse
import os

from . import eeprom
from .factory import create_inky
from .platform import should_use_hardware, get_implementation_type

# Maintain imports for backward compatibility
from .inky_ac073tc1a import Inky as InkyAC073TC1A  # noqa: F401
from .inky_ssd1683 import Inky as InkyWHAT_SSD1683  # noqa: F401
from .inky_uc8159 import Inky as InkyUC8159  # noqa: F401
from .phat import InkyPHAT, InkyPHAT_SSD1608  # noqa: F401
from .what import InkyWHAT  # noqa: F401

DISPLAY_TYPES = ["what", "phat", "phatssd1608", "impressions", "7colour", "whatssd1683", "impressions73"]
DISPLAY_COLORS = ["red", "black", "yellow"]


def auto(i2c_bus=None, ask_user=False, verbose=False, simulation=None):
    """Auto-detect Inky board from EEPROM and return an Inky class instance.
    
    :param i2c_bus: Optional I2C bus for EEPROM detection
    :param ask_user: If True, prompt for display type if not detected
    :param verbose: If True, print verbose information
    :param simulation: Force simulation mode (True/False) or auto-detect (None)
    :return: Appropriate Inky implementation
    """
    # Check for environment variable override
    if simulation is None and os.environ.get("INKY_FORCE_SIMULATION", "").lower() in ("1", "true", "yes"):
        simulation = True
        if verbose:
            print("Simulation mode forced by INKY_FORCE_SIMULATION environment variable")
    
    # Determine if we should use hardware or simulator
    use_hardware = should_use_hardware() if simulation is None else not simulation
    platform_type = get_implementation_type()
    
    if verbose:
        print(f"Platform detected: {platform_type}")
        print(f"Using {'hardware' if use_hardware else 'simulator'} implementation")
    
    # Try to detect display from EEPROM if using hardware
    if use_hardware:
        _eeprom = eeprom.read_eeprom(i2c_bus=i2c_bus)
        
        if _eeprom is not None:
            if verbose:
                print(f"Detected {_eeprom.get_variant()}")
            
            # Map display variant to type and color
            if _eeprom.display_variant in (1, 4, 5):
                return create_inky("phat", _eeprom.get_color(), simulation=simulation, verbose=verbose)
            
            if _eeprom.display_variant in (10, 11, 12):
                return create_inky("phatssd1608", _eeprom.get_color(), simulation=simulation, verbose=verbose)
            
            if _eeprom.display_variant in (2, 3, 6, 7, 8):
                return create_inky("what", _eeprom.get_color(), simulation=simulation, verbose=verbose)
            
            if _eeprom.display_variant == 14:
                return create_inky("impressions", resolution=(600, 448), simulation=simulation, verbose=verbose)
            
            if _eeprom.display_variant in (15, 16):
                return create_inky("impressions", resolution=(640, 400), simulation=simulation, verbose=verbose)
            
            if _eeprom.display_variant in (17, 18, 19):
                return create_inky("whatssd1683", _eeprom.get_color(), resolution=(400, 300), simulation=simulation, verbose=verbose)
            
            if _eeprom.display_variant == 20:
                return create_inky("impressions73", resolution=(800, 480), simulation=simulation, verbose=verbose)
    
    # If we reach here, either:
    # 1. We're in simulation mode
    # 2. No EEPROM was detected
    # 3. The EEPROM contained an unknown display variant
    
    if ask_user:
        if verbose and use_hardware:
            print("Failed to detect an Inky board. Please specify display type and colour.")
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--simulate", "-s", action="store_true", default=False, help="Simulate Inky display")
        parser.add_argument("--type", "-t", type=str, required=True, choices=DISPLAY_TYPES, help="Type of display")
        parser.add_argument("--colour", "-c", type=str, required=False, choices=DISPLAY_COLORS, help="Display colour")
        args, _ = parser.parse_known_args()
        
        # Use the user's simulation preference if provided
        if simulation is None:
            simulation = args.simulate
        
        return create_inky(args.type, args.colour, simulation=simulation, verbose=verbose)
    
    # If we get here, we failed to detect a display and the user didn't specify one
    if use_hardware:
        raise RuntimeError("No EEPROM detected! You must manually initialise your Inky board or enable ask_user.")
    else:
        # Default to impressions simulator if in simulation mode with no detection
        if verbose:
            print("No display type specified, defaulting to impressions simulator")
        return create_inky("impressions", simulation=True, verbose=verbose)
