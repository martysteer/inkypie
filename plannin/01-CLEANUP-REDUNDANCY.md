# 01 — Cleanup: Remove Redundancy and Dead Weight

Priority: HIGH — Do this first, before any refactoring.

## 1.1 Delete Committed __pycache__

```bash
# Remove from git tracking (keeps local files until next clean)
git rm -r --cached inky/__pycache__/
```

Verify `.gitignore` already has `__pycache__/` (it does). Commit this removal.

## 1.2 Remove Mystery / Junk Files

| File | Action | Reason |
|------|--------|--------|
| `.lgd-nfy0` | DELETE | Unknown artifact, zero utility |
| `.DS_Store` (root + examples/) | DELETE + add to .gitignore | macOS cruft |
| `MANIFEST.in` | DELETE | Hatch handles includes via pyproject.toml |
| `gallery.txt` | REVIEW | If identical to `sample_gallery.txt`, delete one |

```bash
git rm .lgd-nfy0
git rm .DS_Store examples/.DS_Store
git rm MANIFEST.in
# Check gallery files:
diff gallery.txt sample_gallery.txt
```

## 1.3 Consolidate Duplicate Drivers

Check whether `ssd1608.py` and `ssd1683.py` are exact copies of `inky_ssd1608.py` / `inky_ssd1683.py`:

```bash
diff inky/ssd1608.py inky/inky_ssd1608.py
diff inky/ssd1683.py inky/inky_ssd1683.py
```

**If identical:** delete the shorter-named versions and grep for any imports of them.
**If different:** determine which is canonical and consolidate.

## 1.4 Retire `mock.py` or Make It Import-Safe

`mock.py` does `from . import inky, inky_uc8159` at module level — these are hardware drivers
that fail on macOS. The tests (`test_simulator.py`) test only `mock.py`.

**Options (pick one):**
- **(A) Delete `mock.py`** — Replace all references with `simulator.py`/`simple_simulator.py`.
  Update tests to test the new simulators. This is the cleanest path.
- **(B) Guard the imports** — Wrap `from . import inky` in try/except so `mock.py` can be
  imported on macOS. Keep for backwards compat but mark deprecated.

**Recommended: Option A.** The `__init__.py` already provides `InkyMockPHAT`/`InkyMockWHAT`
fallbacks using `InkySimpleSimulator`. Delete `mock.py`, update tests.

## 1.5 Remove Duplicate InkyMock from Story Builder

`inky_story_builder.py` contains its own `class InkyMock` (lines ~130-145). This duplicates
`InkySimpleSimulator`. Replace with:

```python
from inky import create_inky
# ...
inky_display = create_inky("impressions", simulation=True)
```

This makes the story builder use the same code path as the image viewer.

## 1.6 Consolidate Documentation

| File | Action |
|------|--------|
| `README-platform-update.md` | Merge useful content into `README.md`, then DELETE |
| `INSTALL.md` | Merge into `README.md` install section, then DELETE |
| `.rubric/` | Archive to `.rubric/ARCHIVED/` or delete — the plan is implemented |
| `.rubric/project_structure.md` | Stale, describes old structure. DELETE |
| `.rubric/requirements_tracker.md` | Stale. DELETE or update into ROADMAP.md |

## 1.7 Clean Up Shell Scripts

| Script | Action |
|--------|--------|
| `install.sh` | KEEP — This is the upstream Pimoroni installer pattern, well-written |
| `setup.sh` | DELETE — Overlaps with `install.sh` and the Makefile `pyenv` target |
| `uninstall.sh` | KEEP — Paired with install.sh |
| `check.sh` | KEEP — Used by `make check` and CI |

## 1.8 Update `.gitignore`

Add these entries:

```gitignore
# macOS
.DS_Store

# Already there but double-check:
__pycache__/
.venv/
*.pyc

# IDE
.vscode/
```

## Commit Message

```
chore: remove dead files, __pycache__, and consolidate duplicates

- Remove committed __pycache__ from tracking
- Delete .lgd-nfy0, .DS_Store files, MANIFEST.in
- Remove duplicate ssd1608.py/ssd1683.py (if confirmed dupes)
- Merge README-platform-update.md and INSTALL.md into README.md
- Delete stale .rubric planning docs
- Delete setup.sh (superseded by Makefile + install.sh)
```
