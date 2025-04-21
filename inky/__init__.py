"""Inky e-Ink Display Drivers."""

# Base classes and utilities
from .base import BaseInky  # noqa: F401
from .platform import is_raspberry_pi, get_implementation_type  # noqa: F401
from .factory import create_inky  # noqa: F401

# Colors
from .inky import BLACK, RED, WHITE, YELLOW  # noqa: F401
from .inky_uc8159 import BLACK, WHITE, GREEN, BLUE, RED, YELLOW, ORANGE, CLEAN  # noqa: F401

# Auto-detection
from .auto import auto  # noqa: F401

# Core hardware classes (maintained for backward compatibility)
from . import inky  # noqa: F401
from .inky_ac073tc1a import Inky as Inky_Impressions_7  # noqa: F401
from .inky_ssd1683 import Inky as InkyWHAT_SSD1683  # noqa: F401
from .inky_uc8159 import Inky as Inky7Colour  # noqa: F401
from .phat import InkyPHAT, InkyPHAT_SSD1608  # noqa: F401
from .what import InkyWHAT  # noqa: F401

# Simulators
from .simulator import InkySimulator  # noqa: F401
from .simple_simulator import InkySimpleSimulator  # noqa: F401

# Legacy mock classes (maintained for backward compatibility)
from .mock import InkyMockPHAT, InkyMockWHAT  # noqa: F401

__version__ = "2.0.0"

# For backward compatibility with namespace packages
try:
    from pkg_resources import declare_namespace
    declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
