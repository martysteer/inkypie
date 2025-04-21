"""Platform detection for Inky library."""
import os
import platform

def is_raspberry_pi():
    """Detect if running on Raspberry Pi hardware."""
    return (
        platform.system() == "Linux" and 
        os.path.exists("/proc/device-tree/model") and
        "raspberry pi" in open("/proc/device-tree/model").read().lower()
    )

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
