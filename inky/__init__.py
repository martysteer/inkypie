"""Inky e-Ink Display Drivers."""

# Import platform detection utilities first to check environment
from .platform import is_raspberry_pi, get_implementation_type, is_simulation_forced

# Basic color constants that should work regardless of platform
BLACK = 0
WHITE = 1
RED = YELLOW = 2
GREEN = 2
BLUE = 3
ORANGE = 6
CLEAN = 7

# Base class and utilities
from .base import BaseInky  # noqa: F401

# Factory functions for creating displays
from .factory import create_inky  # noqa: F401

# Auto-detection
from .auto import auto  # noqa: F401

# Simulators
from .simulator import InkySimulator  # noqa: F401
from .simple_simulator import InkySimpleSimulator  # noqa: F401

# Import hardware-dependent modules only if on Raspberry Pi
# and simulation is not forced
if is_raspberry_pi() and not is_simulation_forced():
    try:
        # Core hardware classes
        from . import inky  # noqa: F401
        from .inky_ac073tc1a import Inky as Inky_Impressions_7  # noqa: F401
        from .inky_ssd1683 import Inky as InkyWHAT_SSD1683  # noqa: F401
        from .inky_uc8159 import Inky as Inky7Colour  # noqa: F401
        from .phat import InkyPHAT, InkyPHAT_SSD1608  # noqa: F401
        from .what import InkyWHAT  # noqa: F401
        
        # Additional color constants from hardware modules
        # (will override the basic ones defined above)
        from .inky import BLACK, RED, WHITE, YELLOW  # noqa: F401
        from .inky_uc8159 import BLACK, WHITE, GREEN, BLUE, RED, YELLOW, ORANGE, CLEAN  # noqa: F401
    except ImportError as e:
        print(f"Notice: Hardware modules not fully available - {e}")
        print("Running in simulator mode")

# Legacy mock classes (maintained for backward compatibility)
try:
    from .mock import InkyMockPHAT, InkyMockWHAT  # noqa: F401
except ImportError:
    # Create stub mock classes if original ones can't be imported
    class InkyMockPHAT(InkySimpleSimulator):
        """Fallback mock for InkyPHAT."""
        def __init__(self, colour='black'):
            super().__init__(display_type='phat', colour=colour)
    
    class InkyMockWHAT(InkySimpleSimulator):
        """Fallback mock for InkyWHAT."""
        def __init__(self, colour='black'):
            super().__init__(display_type='what', colour=colour)

__version__ = "2.0.0"

# For backward compatibility with namespace packages
try:
    from pkg_resources import declare_namespace
    declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
