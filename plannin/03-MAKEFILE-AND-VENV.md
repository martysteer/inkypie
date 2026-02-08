# 03 — Unified Makefile with pyenv for Local and Pi Environments

Priority: HIGH — This is the developer's daily driver.

## 3.1 Current Makefile Problems

- `pyenv` target refuses to run on macOS (exits with error)
- `pyenv-dev` hardcodes individual pip installs instead of using pyproject.toml extras
- `dev-deps` calls `sudo apt install dos2unix shellcheck` — fails on macOS
- No `make setup` one-liner for new developers
- No `make run-viewer` or `make run-story` convenience targets
- `clean` deletes .venv but doesn't clean __pycache__

## 3.2 Proposed Makefile (Complete Rewrite)

```makefile
LIBRARY_NAME := $(shell hatch project metadata name 2>/dev/null || echo "inky")
LIBRARY_VERSION := $(shell hatch version 2>/dev/null || echo "unknown")
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Platform detection
UNAME_S := $(shell uname -s)
IS_MACOS := $(filter Darwin,$(UNAME_S))
IS_PI := $(shell test -f /proc/device-tree/model && grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null && echo yes)

.PHONY: help venv venv-pi install dev lint test qa check clean run-viewer run-story build deploy

help:  ## Show this help
	@echo "$(LIBRARY_NAME) v$(LIBRARY_VERSION)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ─── Environment Setup ────────────────────────────────────

venv: $(VENV)/bin/activate  ## Create venv (macOS/dev — no hardware deps)

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
ifdef IS_PI
	$(PIP) install -e ".[hardware,simulator,apps,dev]"
else
	$(PIP) install -e ".[simulator,apps,dev]"
endif
	@echo ""
	@echo "✅ Virtual environment ready. Activate with:"
	@echo "   source $(VENV)/bin/activate"

venv-pi: ## Create venv with all Pi hardware deps (Raspberry Pi only)
ifndef IS_PI
	$(error This target requires a Raspberry Pi. Use 'make venv' for macOS/dev.)
endif
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[hardware,simulator,apps,examples,dev]"
	@echo "✅ Pi environment ready."

install: ## Install package from source (into active env)
	pip install -e "."

# ─── Development ──────────────────────────────────────────

lint: ## Run linters (ruff, isort, codespell)
	$(PYTHON) -m ruff check .
	$(PYTHON) -m isort --check .
	$(PYTHON) -m codespell .

test: ## Run pytest
	$(PYTHON) -m pytest tests/ -v

qa: ## Full QA: lint + test + build check
	$(PYTHON) -m ruff check .
	$(PYTHON) -m isort --check .
	$(PYTHON) -m codespell .
	$(PYTHON) -m build --no-isolation
	$(PYTHON) -m twine check dist/*

check: ## Run check.sh (whitespace, changelog, etc.)
	@bash check.sh

# ─── Run Apps ─────────────────────────────────────────────

run-viewer: ## Run image viewer (simulation mode)
	$(PYTHON) inky_image_viewer.py --simulation --verbose \
		--gallery-file sample_gallery.txt

run-story: ## Run story builder (simulation mode)
	$(PYTHON) inky_story_builder.py --simulation --verbose

# ─── Build & Deploy ───────────────────────────────────────

build: check ## Build distribution packages
	hatch build

tag: ## Tag the current version in git
	git tag -a "v$(LIBRARY_VERSION)" -m "Version $(LIBRARY_VERSION)"

testdeploy: build ## Upload to test PyPI
	twine upload --repository testpypi dist/*

deploy: build ## Upload to PyPI
	twine upload dist/*

# ─── Cleanup ──────────────────────────────────────────────

clean: ## Remove build artifacts, venv, caches
	rm -rf dist build *.egg-info
	rm -rf $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .tox .coverage .pytest_cache

version: ## Show current version
	@echo "$(LIBRARY_NAME) $(LIBRARY_VERSION)"
```

## 3.3 Key Design Decisions

1. **Single `make venv`** — Auto-detects platform, installs correct extras
2. **`make venv-pi`** — Explicit Pi target with hardware deps, errors on non-Pi
3. **All deps from `pyproject.toml`** — No more hardcoded pip install lists
4. **`-e .`** (editable install) — So changes to `inky/` are reflected immediately
5. **`make run-viewer` / `make run-story`** — Zero-friction app testing
6. **`make clean`** — Also kills `__pycache__` dirs recursively

## 3.4 Developer Onboarding Flow

After this refactor, a new developer does:

```bash
git clone https://github.com/martysteer/inkypie.git
cd inkypie
make venv
source .venv/bin/activate
make run-viewer   # See it working immediately
```

On a Pi:
```bash
make venv-pi
source .venv/bin/activate
python inky_image_viewer.py --url https://example.com/photo.jpg
```

## 3.5 Delete `setup.sh`

`setup.sh` is now fully superseded by `make venv-pi` + `install.sh`. Delete it.
