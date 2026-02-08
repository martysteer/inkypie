# 07 — Documentation Consolidation

Priority: LOW — Do last, after everything else works.

## 7.1 Current Doc Sprawl

| Document | Lines | Status |
|----------|-------|--------|
| `README.md` | 151 | Reasonable but missing dev setup |
| `README-platform-update.md` | 140 | Duplicates README, should be merged |
| `INSTALL.md` | 124 | Outdated, different button controls |
| `CHANGELOG.md` | 119 | Upstream history, needs fork entries |
| `.rubric/README.md` | 24 | Actually about samples, misplaced |
| `.rubric/Staged Implementation Plan` | 142 | Done — archive or delete |
| `.rubric/project_structure.md` | 60 | Stale structure description |
| `.rubric/requirements_tracker.md` | 76 | Stale tracker |
| `samples/README.md` | ? | Sample images info |
| `twines/` | — | No README at all |

That's 6 markdown files competing to explain the project, and none of them tell
a new developer how to get started in 2025.

## 7.2 Target Documentation

After consolidation:

```
README.md              # THE doc — what it is, quickstart, architecture, contributing
CHANGELOG.md           # Updated with fork changes
LICENSE                # Keep as-is
samples/README.md      # Keep as-is
twines/README.md       # NEW — explain the story experiments
```

Everything else gets deleted or merged into README.md.

## 7.3 README.md Structure

```markdown
# InkyPie

Extended fork of [pimoroni/inky](https://github.com/pimoroni/inky) with
cross-platform simulation, development tools, and e-ink applications.

## Quick Start

### macOS / Linux (development)
    git clone https://github.com/martysteer/inkypie.git
    cd inkypie
    make venv
    source .venv/bin/activate
    make run-viewer

### Raspberry Pi (with hardware)
    git clone https://github.com/martysteer/inkypie.git
    cd inkypie
    make venv-pi
    source .venv/bin/activate
    python inky_image_viewer.py --url https://example.com/photo.jpg

## What's In the Box

### Core Library (inky/)
Cross-platform Inky display drivers with automatic hardware/simulator detection.
    from inky import auto, create_inky
    display = auto()              # Auto-detect hardware or simulator
    display = create_inky("impressions", simulation=True)  # Force simulator

### Image Viewer (inky_image_viewer.py)
Display images from files, URLs, or galleries on any Inky display.

### Story Builder (inky_story_builder.py)
Interactive triplet-based story generator for e-ink displays.

### Development Tools
    from inky.debug import InkyDebugger, FastModeEnabler

## Architecture
[Brief description of platform.py → factory.py → auto.py flow]
[Display types and their classes]

## Environment Variables
- INKY_FORCE_SIMULATION=1 — Force simulator even on Pi

## Hardware Setup (Raspberry Pi)
[SPI/I2C config, condensed from current README]

## Contributing
    make venv
    source .venv/bin/activate
    make lint          # Check code style
    make test          # Run tests
    make qa            # Full quality assurance

## Upstream
This is a fork of pimoroni/inky. To sync with upstream:
    git fetch upstream
    git merge upstream/main

## License
MIT
```

## 7.4 CHANGELOG.md

Add a section at the top for the fork's changes:

```markdown
2.1.0-dev (inkypie fork)
------------------------
* New: Cross-platform simulator (pygame + PIL fallback)
* New: Platform detection and factory pattern
* New: BaseInky abstract base class
* New: Debug tools (InkyDebugger, FastModeEnabler)
* New: Image viewer app with gallery and button navigation
* New: Story builder app with triplet-based narrative generation
* New: Makefile with pyenv targets for macOS and Pi
* Enhancement: Auto-detect hardware vs simulator
* Enhancement: Environment variable to force simulation mode
```

## 7.5 twines/README.md (New)

```markdown
# Twine Story Experiments

Experimental story data and Twee-format files for the Inky Story Builder.

## Files

- `story_data.json` — Structured story data used by `inky_story_builder.py`
- `*.twee` — Twine/Twee format story experiments (not used by Python code)
- `eink-story-ui.html` — Standalone HTML prototype of the triplet builder
- `story-triplet-script.py` — Standalone CLI story script

## Background

These files were created during design exploration for the e-ink story builder,
using a combination of manual writing and AI-assisted brainstorming.
```
