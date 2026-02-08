# 08 — Execution Order and Checklist

## Dependency Graph

```
01-CLEANUP ──→ 02-PACKAGE ──→ 03-MAKEFILE ──→ 04-LIBRARY ──→ 05-APPS
                                                    │             │
                                                    └──→ 06-TESTS ┘
                                                              │
                                                         07-DOCS
```

## Phase 1: Foundation (do first, commit each step)

### Step 1.1 — Cleanup (01-CLEANUP-REDUNDANCY.md)
- [ ] `git rm -r --cached inky/__pycache__/`
- [ ] Delete `.lgd-nfy0`, `.DS_Store` files, `MANIFEST.in`
- [ ] Diff and resolve `ssd1608.py` vs `inky_ssd1608.py` (and ssd1683 pair)
- [ ] Delete `setup.sh`
- [ ] Delete or archive `.rubric/` stale docs
- [ ] Update `.gitignore`
- [ ] Commit: `chore: remove dead files and committed __pycache__`

### Step 1.2 — Package & Deps (02-PACKAGE-AND-DEPS.md)
- [ ] Rewrite `pyproject.toml` dependencies with optional-dependencies groups
- [ ] Update fork identity (maintainer, URLs)
- [ ] Delete `requirements-dev.txt`
- [ ] Simplify or delete `requirements.txt`
- [ ] Update `tox.ini` to use extras
- [ ] Bump version to `2.1.0-dev`
- [ ] Commit: `build: restructure dependencies with platform-conditional extras`

### Step 1.3 — Makefile & venv (03-MAKEFILE-AND-VENV.md)
- [ ] Rewrite `Makefile` with unified venv target
- [ ] Test `make venv` on macOS — verify `pip install -e ".[simulator,apps,dev]"` works
- [ ] Test `make clean` removes all caches
- [ ] Test `make lint`, `make test` work in the venv
- [ ] Commit: `build: unified Makefile with platform-aware venv targets`

## Phase 2: Refactoring (do after Phase 1 is stable)

### Step 2.1 — Library (04-LIBRARY-REFACTOR.md)
- [ ] Clean up `__init__.py` — remove fragile conditional imports
- [ ] Delete `mock.py` (or guard its imports)
- [ ] Create `constants.py` with canonical colour definitions
- [ ] Simplify simulator fallback (InkySimulator.__new__ pattern)
- [ ] Clean up redundant imports in `auto.py`
- [ ] Commit: `refactor: clean up inky/ module imports and colour constants`

### Step 2.2 — Apps (05-APPS-REFACTOR.md)
- [ ] Remove `sys.path` hack from image viewer
- [ ] Remove inline `InkyMock` from story builder
- [ ] Remove inline `IS_SIMULATION` detection from story builder
- [ ] Extract story data to `twines/story_data.json` (verify match)
- [ ] Fix `set_image` introspection hack in image viewer
- [ ] Optionally extract shared ButtonHandler
- [ ] Optionally move apps to `apps/` directory
- [ ] Commit: `refactor: clean up apps, use library factory and shared code`

## Phase 3: Quality (do after Phase 2)

### Step 3.1 — Tests (06-TESTS-AND-CI.md)
- [ ] Write `test_platform.py`
- [ ] Write `test_factory.py`
- [ ] Write `test_simple_simulator.py`
- [ ] Write `test_base.py`
- [ ] Update or delete `test_simulator.py` (if mock.py removed)
- [ ] Fix CI workflows (remove sudo apt from dev-deps, fix qa.yml typo)
- [ ] Add Python 3.12 to test matrix
- [ ] Commit: `test: add tests for platform, factory, and simulator modules`

### Step 3.2 — Docs (07-DOCS-CONSOLIDATION.md)
- [ ] Merge `README-platform-update.md` into `README.md`
- [ ] Merge `INSTALL.md` into `README.md`
- [ ] Delete merged docs
- [ ] Add fork changelog entry
- [ ] Create `twines/README.md`
- [ ] Commit: `docs: consolidate into single README, update changelog`

## Final Verification

After all phases:
```bash
make clean
make venv
source .venv/bin/activate
make lint          # Should pass
make test          # Should pass
make run-viewer    # Should launch simulator
make run-story     # Should launch simulator
make qa            # Should pass (may need check.sh adjustments)
```

## Estimated Effort

| Phase | Effort | Risk |
|-------|--------|------|
| 1.1 Cleanup | 30 min | Low |
| 1.2 Package | 1 hour | Medium (dep resolution) |
| 1.3 Makefile | 30 min | Low |
| 2.1 Library | 2 hours | Medium (import chain) |
| 2.2 Apps | 1 hour | Low |
| 3.1 Tests | 2 hours | Low |
| 3.2 Docs | 1 hour | Low |
| **Total** | **~8 hours** | |
