# 00 — Project Audit: Current State of InkyPie

## What This Project Is

InkyPie is a fork of [pimoroni/inky](https://github.com/pimoroni/inky) (upstream) with added
cross-platform simulation, a factory/auto-detect pattern, an image viewer app, a story builder
app, and Twine-based story experiments. It lives at `github.com/martysteer/inkypie`.

## Architecture Overview

```
inkypie/
├── inky/                  # Core library (forked from pimoroni/inky + new modules)
│   ├── __init__.py        # Heavy conditional imports, colour constants, version
│   ├── auto.py            # Auto-detect display via EEPROM + factory fallback
│   ├── base.py            # ABC BaseInky (NEW — added in refactoring)
│   ├── platform.py        # Platform detection: is_raspberry_pi(), etc. (NEW)
│   ├── factory.py         # create_inky() factory function (NEW)
│   ├── simulator.py       # Pygame-based simulator (NEW)
│   ├── simple_simulator.py # PIL-only fallback simulator (NEW)
│   ├── debug.py           # InkyDebugger + FastModeEnabler (NEW)
│   ├── mock.py            # Legacy tkinter-based mocks (ORIGINAL upstream)
│   ├── inky.py            # Original upstream hardware driver
│   ├── inky_uc8159.py     # UC8159 7-colour driver (upstream)
│   ├── inky_ssd1608.py    # SSD1608 driver (upstream)
│   ├── inky_ssd1683.py    # SSD1683 driver (upstream)
│   ├── inky_ac073tc1a.py  # AC073TC1A 7.3" driver (upstream)
│   ├── phat.py            # InkyPHAT classes (upstream)
│   ├── what.py            # InkyWHAT classes (upstream)
│   ├── ssd1608.py         # Appears to be duplicate/alt of inky_ssd1608
│   ├── ssd1683.py         # Appears to be duplicate/alt of inky_ssd1683
│   ├── eeprom.py          # EEPROM reading (upstream)
│   └── __pycache__/       # ⚠ Committed to git (should be in .gitignore)
├── inky_image_viewer.py   # Standalone app: gallery viewer with button nav
├── inky_story_builder.py  # Standalone app: triplet story builder for eink
├── twines/                # Twine/Twee story experiments + story_data.json
├── examples/              # Upstream examples + new cross_platform.py
├── tests/                 # Upstream test suite (mostly tests mock.py)
├── samples/               # Sample images for viewer
├── .rubric/               # Internal planning docs
├── .github/workflows/     # CI: build, test, qa, install
├── tools/                 # GIMP palettes
├── hardware/              # Fritzing files
└── [config files]         # Makefile, pyproject.toml, requirements*.txt, etc.
```

## Current State Assessment

### What Works
- The platform detection layer (`platform.py`, `factory.py`, `auto.py`) is implemented
- `BaseInky` ABC exists in `base.py`
- Pygame simulator (`simulator.py`) and PIL fallback (`simple_simulator.py`) exist
- Debug tools (`debug.py`) are implemented
- Image viewer (`inky_image_viewer.py`) is functional
- Story builder (`inky_story_builder.py`) is functional
- Makefile has `pyenv` and `pyenv-dev` targets
- Git working tree is clean

### What's Broken or Half-Done
1. **`__pycache__` is committed** — multiple .pyc files tracked in git
2. **`ssd1608.py` and `ssd1683.py`** — appear to be duplicates of `inky_ssd1608.py`/`inky_ssd1683.py`
3. **`mock.py` imports `inky.inky`** which fails on non-Pi platforms (circular + hardware dep)
4. **`__init__.py`** has fragile conditional imports that silently eat errors
5. **Colour constants** are defined in 4+ places with conflicting values
6. **`inky_story_builder.py`** has its own `InkyMock` class, duplicating `simple_simulator.py`
7. **Three simulator implementations**: `mock.py` (tkinter), `simulator.py` (pygame), `simple_simulator.py` (PIL)
8. **`requirements.txt`** lists `inky>=2.0.0` and `RPi.GPIO` — wrong for a dev env on macOS
9. **`setup.sh`** and `install.sh`** overlap in purpose
10. **Tests only test `mock.py`**, not the new simulator/factory/platform modules
11. **CI workflows** call `make dev-deps` which tries `sudo apt install` (fails on macOS)
12. **`pyproject.toml`** still lists upstream author/URLs, not the fork's identity
13. **`.rubric/` docs** are stale — describe the plan as future but Stage 1-3 are already done
14. **`README-platform-update.md`** duplicates content from main `README.md`
15. **`INSTALL.md`** is outdated (references old button controls, different workflow)
16. **Twines directory** is experimental and undocumented
17. **`.lgd-nfy0`** — mystery file at project root
18. **`gallery.txt`** and `sample_gallery.txt`** — two gallery files with unclear distinction
19. **`MANIFEST.in`** — exists but hatch handles build includes via `pyproject.toml`

### Dependency Confusion

There are currently **4 separate dependency specifications**:
- `pyproject.toml` `[project].dependencies` — numpy, pillow, smbus2, spidev, gpiodevice (Pi-only)
- `requirements.txt` — inky>=2.0.0, RPi.GPIO, pillow, requests, geocoder, seaborn, wikiquotes
- `requirements-dev.txt` — ruff, hatch, tox, etc.
- `requirements-examples.txt` — pillow, fonts, geocoder, seaborn, wikiquotes

The `requirements.txt` tries to install the published `inky` package AND RPi.GPIO, making it
useless on macOS. The `pyproject.toml` deps are Pi-only hardware libs. Nothing cleanly supports
"install this repo as a dev package on macOS".

### Staging Plan Completion (from `.rubric/`)
- ✅ Stage 1: Base class + platform detection — Done
- ✅ Stage 2: Enhanced simulators — Done (pygame + PIL)
- ✅ Stage 3: Factory pattern + auto — Done
- ⚠ Stage 4: Debug tools — Partially done (debug.py exists but untested)
- ❌ Stage 5: Documentation + examples — Not done
