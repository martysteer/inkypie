# 02 — Fix Packaging, Dependencies, and pyproject.toml

Priority: HIGH — This is what makes `pip install -e .` and the venv actually work.

## 2.1 The Core Problem

The project has **two identities**:

1. **Upstream `inky` library** — A pip-installable driver package for Pi hardware
2. **`inkypie` fork** — A development workspace with apps, simulators, and experiments

Currently `pyproject.toml` declares `name = "inky"` with Pi-only deps (smbus2, spidev,
gpiodevice), and `requirements.txt` tries to `pip install inky` from PyPI. Neither works
cleanly for local development on macOS.

## 2.2 Decision: Keep the Package Name as `inky`

Since this is a fork that should remain compatible with upstream, keep `name = "inky"` in
`pyproject.toml` but make deps platform-conditional so it installs on macOS too.

## 2.3 Rewrite `pyproject.toml` Dependencies

Replace the flat deps list with platform-conditional dependencies:

```toml
[project]
name = "inky"
# ...
dependencies = [
    "numpy",
    "pillow>=9.0.0",
]

[project.optional-dependencies]
# Hardware deps — only needed on Pi
hardware = [
    "smbus2",
    "spidev",
    "gpiodevice>=0.0.3",
    "RPi.GPIO>=0.7.0",
]
# Simulator deps
simulator = [
    "pygame",
]
# App deps — for image viewer and story builder
apps = [
    "requests>=2.27.0",
]
# Example deps
examples = [
    "beautifulsoup4>=4.10.0",
    "fonts",
    "font-source-sans-pro",
    "font-source-serif-pro",
    "font-fredoka-one",
    "font-hanken-grotesk",
    "font-intuitive",
    "geocoder>=1.38.0",
    "seaborn>=0.11.0",
    "wikiquotes>=1.0.0",
]
# Dev deps
dev = [
    "check-manifest",
    "ruff",
    "codespell",
    "isort",
    "twine",
    "hatch",
    "hatch-fancy-pypi-readme",
    "hatch-requirements-txt",
    "tox",
    "pdoc",
    "pytest>=3.1",
    "pytest-cov",
    "coverage",
    "mock",
    "build",
]
```

## 2.4 Simplify Requirements Files

After moving everything into `pyproject.toml` optional-dependencies:

| File | Action |
|------|--------|
| `requirements.txt` | REWRITE — Just `.[apps,simulator]` or delete entirely |
| `requirements-dev.txt` | DELETE — Use `pip install -e ".[dev]"` |
| `requirements-examples.txt` | KEEP (referenced by hatch metadata hook) — but sync with pyproject.toml |

Ideally, reduce to:

```
# requirements.txt — for quick install reference
-e ".[apps,simulator]"
```

Or even better, delete `requirements.txt` and `requirements-dev.txt` entirely and document
the install commands in the Makefile and README.

## 2.5 Update Fork Identity

In `pyproject.toml`, update:

```toml
[project]
description = "Inky e-Paper Display Drivers — extended fork with simulators and apps"

authors = [
    { name = "Philip Howard", email = "phil@pimoroni.com" },
]
maintainers = [
    { name = "Marty Steer" },
]

[project.urls]
GitHub = "https://github.com/martysteer/inkypie"
Upstream = "https://github.com/pimoroni/inky"
```

## 2.6 Update Version

Currently `__version__ = "2.0.0"` in `__init__.py`. The upstream CHANGELOG goes to 2.0.0.
Since this fork extends beyond upstream, bump to something like:

```python
__version__ = "2.1.0-dev"
```

And add a corresponding entry to `CHANGELOG.md`.

## 2.7 Fix `tox.ini`

The `[testenv:qa]` section references `-r{toxinidir}/requirements-dev.txt`. If we delete
that file, update tox to use extras instead:

```ini
[testenv:qa]
extras = dev
commands =
    check-manifest
    python -m build --no-isolation
    python -m twine check dist/*
    isort --check .
    ruff check .
    codespell .
```

## 2.8 Fix hatch Requirements Hook

`pyproject.toml` has:
```toml
[tool.hatch.metadata.hooks.requirements_txt.optional-dependencies]
example-depends = ["requirements-examples.txt"]
```

If keeping `requirements-examples.txt`, this is fine. If not, remove this hook and use
`pyproject.toml` `[project.optional-dependencies]` directly.
