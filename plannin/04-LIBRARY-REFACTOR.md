# 04 — Library Refactor: Consolidate inky/ Module

Priority: MEDIUM — Do after cleanup (01) and packaging (02).

## 4.1 Problem Summary

The `inky/` package has grown organically from the upstream Pimoroni code plus the new
cross-platform additions. The result is:

- **3 simulator implementations** that partially overlap
- **Colour constants defined in 5+ places** with inconsistent values
- **`__init__.py`** that does heavy conditional imports with silent error swallowing
- **`mock.py`** that can't even be imported on macOS
- **Duplicated driver files** (ssd1608.py vs inky_ssd1608.py)

## 4.2 Target Module Structure

```
inky/
├── __init__.py           # Clean re-exports, version, constants
├── base.py               # BaseInky ABC (keep as-is, it's clean)
├── platform.py           # Platform detection (keep as-is, it's clean)
├── factory.py            # create_inky() factory (minor cleanup)
├── auto.py               # auto() detection (minor cleanup)
├── eeprom.py             # EEPROM reading (keep as-is, upstream)
├── simulator.py          # PRIMARY simulator — pygame with PIL fallback
├── debug.py              # Debug tools (keep as-is, works well)
├── drivers/              # NEW subdirectory for hardware drivers
│   ├── __init__.py
│   ├── inky.py           # Base hardware driver
│   ├── uc8159.py         # 7-colour driver
│   ├── ssd1608.py        # SSD1608 driver
│   ├── ssd1683.py        # SSD1683 driver
│   ├── ac073tc1a.py      # 7.3" driver
│   ├── phat.py           # InkyPHAT
│   └── what.py           # InkyWHAT
└── [no mock.py]          # Deleted — replaced by simulator.py
```

**Alternative (simpler, less churn):** Keep drivers flat in `inky/` but just clean up the
naming and remove duplicates. This avoids breaking upstream test expectations.

## 4.3 Simplify `__init__.py`

Current `__init__.py` is 72 lines of conditional imports that silently catch errors.
Replace with a clean, predictable structure:

```python
"""Inky e-Ink Display Drivers."""
__version__ = "2.1.0-dev"

# Colour constants (canonical source of truth)
BLACK = 0
WHITE = 1
RED = YELLOW = 2
GREEN = 2
BLUE = 3
ORANGE = 6
CLEAN = 7

# Platform detection
from .platform import is_raspberry_pi, is_simulation_forced

# Core API — always available
from .base import BaseInky
from .factory import create_inky
from .auto import auto
from .simulator import InkySimulator
from .simple_simulator import InkySimpleSimulator

# Hardware classes — import only on Pi, but expose names for isinstance checks
if is_raspberry_pi() and not is_simulation_forced():
    try:
        from .inky_uc8159 import Inky as Inky7Colour
        from .inky_ac073tc1a import Inky as Inky_Impressions_7
        from .inky_ssd1683 import Inky as InkyWHAT_SSD1683
        from .phat import InkyPHAT, InkyPHAT_SSD1608
        from .what import InkyWHAT
    except ImportError:
        pass  # Hardware libs not installed; simulators still work

# Legacy compat aliases
InkyMockPHAT = InkySimpleSimulator
InkyMockWHAT = InkySimpleSimulator
```

Key changes:
- No more `from . import inky` (the module name clashes with the package)
- No silent re-definition of colour constants from hardware modules
- Legacy mock names point to the simple simulator
- Clean, predictable import order

## 4.4 Clean Up Colour Constants

Currently BLACK/WHITE/RED etc. are defined in: `__init__.py`, `base.py`, `mock.py`,
`inky.py`, `inky_uc8159.py`, and each simulator. The values **conflict** — e.g.,
`base.py` has `GREEN = 2` but `inky_uc8159.py` has `GREEN = 2` (same), however
`RED = 2` in base but `RED = 4` in uc8159.

**Fix:** Define two canonical constant sets and document them:

```python
# inky/constants.py (NEW)

# 2-colour / 3-colour displays (pHAT, wHAT)
class InkyColours:
    WHITE = 0
    BLACK = 1
    RED = 2
    YELLOW = 2

# 7-colour displays (Impression, UC8159)
class Inky7Colours:
    BLACK = 0
    WHITE = 1
    GREEN = 2
    BLUE = 3
    RED = 4
    YELLOW = 5
    ORANGE = 6
    CLEAN = 7
```

Each display class uses the appropriate set. The top-level `__init__.py` exports
the 7-colour set (superset) for backward compat.

## 4.5 Merge Simulator Fallback Logic

`simulator.py` already has fallback logic to `simple_simulator.py`. But it's convoluted
with `_check_pygame()` delegation on every method call.

**Simplify:** Make `simulator.py` the single entry point. If pygame isn't available,
return an `InkySimpleSimulator` instance directly from `InkySimulator.__new__`:

```python
class InkySimulator(BaseInky):
    def __new__(cls, *args, **kwargs):
        if not PYGAME_AVAILABLE:
            return InkySimpleSimulator(*args, **kwargs)
        return super().__new__(cls)
```

This eliminates all the `_check_pygame` boilerplate.

## 4.6 Fix `factory.py` Imports

`factory.py` uses string-based dynamic imports (`"inky.phat.InkyPHAT"`). This works
but is fragile. Since the factory already handles ImportError gracefully, this is
acceptable — just clean up the mappings if any driver files are renamed/moved.

## 4.7 Update `auto.py`

`auto.py` re-imports hardware classes at module level behind `if is_raspberry_pi()`.
This is redundant — the factory already handles this. Remove the conditional imports
from `auto.py` and let the factory do the work. `auto()` should just be a thin wrapper
around EEPROM detection + `create_inky()`.
