# InkyPie Project Structure

## Directory Structure

```
inkypie/
├── .rubrick/                     # Project tracking and documentation
│   ├── requirements_tracker.md   # Tracks dependencies and features
│   └── project_structure.md      # This file - describes project organization
├── samples/                      # Sample images for testing
│   └── README.md                 # Information about sample images
├── inky_image_viewer.py          # Main script for displaying images
├── setup.sh                      # Installation script
├── requirements.txt              # Python package dependencies
├── README.md                     # Project documentation
└── LICENSE                       # MIT License
```

## File Descriptions

### Core Files

- **inky_image_viewer.py**: The main Python script that handles image loading, processing, and display on Inky e-paper screens. Includes button control functionality.
  
- **setup.sh**: Bash script to set up the Raspberry Pi environment, enable required interfaces, and install dependencies.

- **requirements.txt**: Lists all Python package dependencies, both required and optional.

### Documentation

- **README.md**: Main project documentation with usage instructions.

- **.rubrick/requirements_tracker.md**: Tracks project requirements, dependencies, and feature implementation status.

- **.rubrick/project_structure.md**: Documents the project's organization (this file).

- **samples/README.md**: Information about sample images and usage recommendations.

### Other

- **LICENSE**: MIT License file.

## Development Approach

The project follows these principles:

1. **Modularity**: Keep core functionality separate from extensions
2. **Progressive enhancement**: Basic features work without optional dependencies
3. **Documentation**: Maintain clear documentation for all aspects of the project
4. **Testing**: Ensure compatibility with all Inky display types

## Adding New Features

When adding new features:

1. Update `.rubrick/requirements_tracker.md` with the new feature and dependencies
2. Add any new dependencies to `requirements.txt`
3. Implement the feature in a backward-compatible way
4. Update documentation as needed
