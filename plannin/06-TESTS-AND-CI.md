# 06 — Fix Tests and CI

Priority: MEDIUM — Do alongside or after library refactor (04).

## 6.1 Current Test State

```
tests/
├── conftest.py              # Mocks for GPIO, smbus2, spidev, tkinter, PIL
├── tools.py                 # MockSMBus helper
├── test_auto.py             # Tests auto() with EEPROM detection
├── test_eeprom.py           # Tests EEPROM encoding/decoding
├── test_init.py             # Tests __init__.py imports
├── test_install_helpers.py  # Tests import errors when libs missing
├── test_set_image.py        # Tests set_image on hardware drivers
├── test_simulator.py        # Tests mock.py (NOT simulator.py!)
```

### Problems
1. **`test_simulator.py` tests `mock.py`** — not the actual simulators
2. **`test_auto.py` assumes hardware imports** — imports `Inky7Colour`, `InkyPHAT` etc.
   directly from `inky`, which fails on macOS without mocked hardware modules
3. **No tests for**: `platform.py`, `factory.py`, `simulator.py`, `simple_simulator.py`,
   `debug.py`, `base.py`
4. **Tests assume Pi-like environment** — the conftest mocks hardware, but the test structure
   is tightly coupled to the upstream hardware-only architecture

## 6.2 New Tests Needed

### `test_platform.py`
```python
def test_is_raspberry_pi_returns_bool():
    from inky.platform import is_raspberry_pi
    assert isinstance(is_raspberry_pi(), bool)

def test_get_implementation_type_on_non_pi():
    from inky.platform import get_implementation_type
    # On macOS/CI, should return "simulator"
    assert get_implementation_type() == "simulator"

def test_should_use_hardware_on_non_pi():
    from inky.platform import should_use_hardware
    assert should_use_hardware() is False

def test_simulation_forced_env(monkeypatch):
    monkeypatch.setenv("INKY_FORCE_SIMULATION", "1")
    from inky.platform import is_simulation_forced
    assert is_simulation_forced() is True
```

### `test_factory.py`
```python
def test_create_simulator_inky_impressions():
    from inky.factory import create_simulator_inky
    display = create_simulator_inky("impressions")
    assert display.width == 600
    assert display.height == 448

def test_create_inky_simulation_mode():
    from inky import create_inky
    display = create_inky("phat", "black", simulation=True)
    assert display.width == 212
    assert display.height == 104

def test_create_inky_unknown_type():
    from inky.factory import create_hardware_inky
    import pytest
    with pytest.raises(ValueError):
        create_hardware_inky("nonexistent")
```

### `test_simple_simulator.py`
```python
def test_simple_simulator_init():
    from inky.simple_simulator import InkySimpleSimulator
    sim = InkySimpleSimulator("impressions", "multi")
    assert sim.width == 600
    assert sim.height == 448

def test_simple_simulator_set_pixel():
    from inky.simple_simulator import InkySimpleSimulator
    sim = InkySimpleSimulator()
    sim.set_pixel(0, 0, 1)
    assert sim.buf[0][0] == 1

def test_simple_simulator_set_image():
    from PIL import Image
    from inky.simple_simulator import InkySimpleSimulator
    sim = InkySimpleSimulator()
    img = Image.new("RGB", (sim.width, sim.height), (255, 0, 0))
    sim.set_image(img)  # Should not raise
```

### `test_base.py`
```python
def test_base_inky_is_abstract():
    from inky.base import BaseInky
    import pytest
    with pytest.raises(TypeError):
        BaseInky((100, 100), "black")  # Can't instantiate ABC
```

## 6.3 Fix Existing Tests

### `test_simulator.py`
- If `mock.py` is deleted (per 01), delete this test file too
- OR rename to `test_mock_legacy.py` and skip if mock.py doesn't exist

### `test_auto.py`
- Needs the GPIO/spidev/smbus2 mocks from conftest to work
- These tests are really integration tests for the upstream auto-detect path
- They should still work in CI (Linux) with mocks, but may need adjustment
  after __init__.py cleanup

### conftest.py
- Add a `@pytest.fixture` that provides a simulator instance for non-Pi tests
- Consider splitting into `conftest_hardware.py` and `conftest_simulator.py`

## 6.4 Fix CI Workflows

### `build.yml`, `test.yml`, `qa.yml`
All call `make dev-deps` which runs:
```bash
python3 -m pip install -r requirements-dev.txt
sudo apt install dos2unix shellcheck
```

After the packaging refactor, change to:
```bash
pip install -e ".[dev]"
# Only install apt packages if available:
if command -v apt &> /dev/null; then
    sudo apt install -y dos2unix shellcheck
fi
```

Or better, update the Makefile `dev-deps` target:
```makefile
dev-deps:
	pip install -e ".[dev]"
ifdef IS_LINUX
	sudo apt install -y dos2unix shellcheck
endif
```

### Test matrix
Currently tests Python 3.9, 3.10, 3.11. Consider adding 3.12 since it's current.
Update `pyproject.toml` classifiers to match.

### `qa.yml` typo
```yaml
# CURRENT (typo):
- name: Set up Python '3,11'
# FIX:
- name: Set up Python '3.11'
```

## 6.5 Coverage

Current `tox.ini` runs coverage. After adding new test files, the coverage should
improve significantly. Set a coverage floor (e.g., 60%) in tox or CI.
