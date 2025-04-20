LIBRARY_NAME := $(shell hatch project metadata name 2> /dev/null)
LIBRARY_VERSION := $(shell hatch version 2> /dev/null)
VENV_NAME := .venv

# Detect operating system
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
  OS := macos
  SUDO :=
else ifeq ($(UNAME_S),Linux)
  OS := linux
  SUDO := sudo
  # Check if we're on a Raspberry Pi
  ifneq ($(wildcard /proc/device-tree/model),)
    IS_PI := $(shell grep -q "Raspberry Pi" /proc/device-tree/model && echo "yes" || echo "no")
  else
    IS_PI := no
  endif
else
  OS := unknown
  SUDO := sudo
endif

.PHONY: usage install uninstall check pytest qa build-deps check tag wheel sdist clean dist testdeploy deploy pyenv pyenv-dev
usage:
ifdef LIBRARY_NAME
	@echo "Library: ${LIBRARY_NAME}"
	@echo "Version: ${LIBRARY_VERSION}\n"
else
	@echo "WARNING: You should 'make dev-deps'\n"
endif
	@echo "Usage: make <target>, where target is one of:\n"
	@echo "install:      install the library locally from source"
	@echo "uninstall:    uninstall the local library"
	@echo "dev-deps:     install Python dev dependencies"
	@echo "pyenv:        create a Python virtual environment and install dependencies"
	@echo "              (for Raspberry Pi with hardware support)"
	@echo "pyenv-dev:    create a development environment without hardware dependencies" 
	@echo "              (for macOS or non-Pi systems)"
	@echo "check:        perform basic integrity checks on the codebase"
	@echo "qa:           run linting and package QA"
	@echo "pytest:       run Python test fixtures"
	@echo "clean:        clean Python build and dist directories"
	@echo "build:        build Python distribution files"
	@echo "testdeploy:   build and upload to test PyPi"
	@echo "deploy:       build and upload to PyPi"
	@echo "tag:          tag the repository with the current version\n"

version:
	@hatch version

install:
	./install.sh --unstable

uninstall:
	./uninstall.sh

dev-deps:
	python3 -m pip install -r requirements-dev.txt
	sudo apt install dos2unix shellcheck

pyenv:
ifeq ($(OS),macos)
	@echo "⚠️  Warning: You're on macOS, which doesn't support Raspberry Pi hardware."
	@echo "⚠️  Please use 'make pyenv-dev' instead for a development environment."
	@echo "⚠️  This will skip hardware-dependent packages."
	@exit 1
else
	@echo "Creating Python virtual environment in ${VENV_NAME}..."
	python3 -m venv ${VENV_NAME}
	@echo "Installing dependencies..."
	${VENV_NAME}/bin/pip install --upgrade pip
	${VENV_NAME}/bin/pip install -r requirements.txt
	${VENV_NAME}/bin/pip install -r requirements-examples.txt
	@echo "\nVirtual environment created successfully!"
	@echo "To activate, run: source ${VENV_NAME}/bin/activate"
endif

pyenv-dev:
	@echo "Creating development Python virtual environment in ${VENV_NAME}..."
	python3 -m venv ${VENV_NAME}
	@echo "Installing dependencies (skipping Raspberry Pi hardware libraries)..."
	${VENV_NAME}/bin/pip install --upgrade pip
	@echo "Installing core non-hardware dependencies..."
	${VENV_NAME}/bin/pip install pillow requests beautifulsoup4 geocoder seaborn wikiquotes
	@echo "Installing fonts..."
	${VENV_NAME}/bin/pip install font-source-sans-pro font-source-serif-pro font-fredoka-one font-hanken-grotesk font-intuitive
	@echo "\nDevelopment virtual environment created successfully!"
	@echo "To activate, run: source ${VENV_NAME}/bin/activate"
	@echo "\nNote: Hardware-dependent libraries like 'RPi.GPIO', 'spidev', and 'inky' have been skipped"
	@echo "as they require a Raspberry Pi. You can develop and test non-hardware functionality."

check:
	@bash check.sh

shellcheck:
	shellcheck *.sh

qa:
	tox -e qa

pytest:
	tox -e py

nopost:
	@bash check.sh --nopost

tag: version
	git tag -a "v${LIBRARY_VERSION}" -m "Version ${LIBRARY_VERSION}"

build: check
	@hatch build

clean:
	-rm -r dist
	-rm -rf ${VENV_NAME}

testdeploy: build
	twine upload --repository testpypi dist/*

deploy: nopost build
	twine upload dist/*