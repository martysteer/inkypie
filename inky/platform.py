"""Platform detection for Inky library."""
import os
import sys
import platform

def is_raspberry_pi():
    """Detect if running on Raspberry Pi hardware."""
    # Check for Raspberry Pi-specific files
    if platform.system() == "Linux" and os.path.exists("/proc/device-tree/model"):
        try:
            with open("/proc/device-tree/model") as f:
                return "raspberry pi" in f.read().lower()
        except:
            pass
    return False

def get_implementation_type():
    """Return 'hardware' or 'simulator' based on platform."""
    if is_raspberry_pi():
        return "hardware"
    else:
        return "simulator"

def is_simulation_forced():
    """Check if simulation mode is forced via environment variable."""
    return os.environ.get("INKY_FORCE_SIMULATION", "").lower() in ("1", "true", "yes")

def should_use_hardware():
    """Determine if hardware implementation should be used."""
    return get_implementation_type() == "hardware" and not is_simulation_forced()

# Safe import functions to avoid ImportError on non-Pi platforms
def safe_import(module_name):
    """Try to import a module, return None if not available."""
    try:
        return __import__(module_name)
    except ImportError:
        return None

# Create safe versions of hardware-dependent modules
gpiod = safe_import('gpiod')
gpiodevice = safe_import('gpiodevice')
spidev = safe_import('spidev')
smbus2 = safe_import('smbus2')
