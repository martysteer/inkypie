# 05 — Refactor Apps: Image Viewer and Story Builder

Priority: MEDIUM — Do after library refactor (04).

## 5.1 Common Issues Across Both Apps

1. **Both have their own platform detection** — `IS_SIMULATION` checks instead of using
   `inky.platform`. Should use `from inky import auto, create_inky` consistently.
2. **Both have their own button handling** — Duplicate GPIO setup code. Should share a
   common `ButtonHandler` utility.
3. **`sys.path` manipulation** in image viewer (`sys.path.insert(0, ...)`) — unnecessary
   if the package is installed via `pip install -e .`.
4. **Hardcoded font paths** — Both try `DejaVuSans.ttf` then fall back to default. Should
   have a shared font utility.

## 5.2 Image Viewer Cleanup

### Remove sys.path hack
```python
# DELETE these lines from inky_image_viewer.py:
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
```
Once the package is pip-installed (editable or not), `from inky import ...` just works.

### Use create_inky() consistently
The viewer already uses `auto()` and `create_inky()` — good. But it also does
`from inky import auto, create_inky, is_raspberry_pi` which imports from `__init__.py`.
Make sure these work cleanly after the __init__.py cleanup.

### Extract shared button handling
Both apps have ~40 lines of identical GPIO setup code. Extract to:

```python
# inky/buttons.py (NEW)
class ButtonHandler:
    """GPIO button handler for Inky displays."""
    PINS = [5, 6, 16, 24]  # A, B, C, D
    LABELS = ["A", "B", "C", "D"]
    
    def __init__(self, callbacks=None, debounce=0.5):
        ...
```

### Fix the `set_image` introspection hack
```python
# Current (fragile):
if 'saturation' in self.inky_display.set_image.__code__.co_varnames:
```
Replace with duck typing or the display's colour attribute:
```python
if self.inky_display.colour == "multi":
    self.inky_display.set_image(image, saturation=self.saturation)
else:
    self.inky_display.set_image(image)
```

## 5.3 Story Builder Cleanup

### Remove InkyMock class
Delete the inline `class InkyMock` and use the library's factory:
```python
if args.simulation or IS_SIMULATION:
    inky_display = create_inky("impressions", simulation=True)
else:
    inky_display = auto()
```

### Remove redundant IS_SIMULATION detection
```python
# DELETE:
IS_SIMULATION = platform.system() != "Linux" or not platform.machine().startswith("arm")

# REPLACE WITH:
from inky.platform import is_raspberry_pi
```

### Extract story data to JSON
`STORY_DATA` is a ~100-line dict embedded in the Python file. It already exists separately
as `twines/story_data.json`. Use that:

```python
import json
from pathlib import Path

STORY_DATA_PATH = Path(__file__).parent / "twines" / "story_data.json"
with open(STORY_DATA_PATH) as f:
    STORY_DATA = json.load(f)
```

Verify that `twines/story_data.json` matches the inline data, then delete the inline copy.

### Use shared ButtonHandler
Replace the local `setup_buttons()` / `button_handler()` with the shared utility from
`inky/buttons.py`.

## 5.4 Consider Moving Apps to `apps/` Directory

Currently the two app scripts sit at the project root alongside library config files.
Consider:

```
apps/
├── image_viewer.py    # renamed from inky_image_viewer.py
└── story_builder.py   # renamed from inky_story_builder.py
```

Update Makefile targets and README accordingly. This keeps the root clean.

## 5.5 Twines Directory

The `twines/` directory contains Twee files and story data from ChatGPT-assisted
brainstorming. Current state:

| File | Status |
|------|--------|
| `story_data.json` | KEEP — Used by story builder (after refactor) |
| `*.twee` | EXPERIMENTAL — Not used by any Python code |
| `eink-story-ui.html` | EXPERIMENTAL — Standalone HTML prototype |
| `story-triplet-script.py` | EXPERIMENTAL — Standalone script |

**Recommendation:** Keep `story_data.json`. Move the experimental Twee files to
`twines/experiments/` or add a `twines/README.md` explaining their purpose.

## 5.6 Samples Directory

- `samples/README.md` is fine
- Contains actual images (png, jpg, svg)
- `sample_gallery.txt` at root references URLs
- `gallery.txt` at root — check if it's identical or different

Consolidate: move `sample_gallery.txt` and `gallery.txt` into `samples/` if they're
image galleries, or keep at root if they're meant to be user-facing config files.
