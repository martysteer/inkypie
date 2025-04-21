# InkyPie Project Requirements Tracker

This file tracks requirements and dependencies for the InkyPie project as we build together.

## Core Dependencies

| Dependency | Status | Purpose | Version | Notes |
|------------|--------|---------|---------|-------|
| Inky | Required | E-ink display driver | Latest | The main library for controlling Inky displays |
| RPi.GPIO | Required | GPIO access for buttons | Latest | Manages button inputs |
| Pillow/PIL | Required | Image processing | Latest | Handles image loading, resizing, and manipulation |

## Optional Dependencies

| Dependency | Status | Purpose | Version | Notes |
|------------|--------|---------|---------|-------|
| requests | Optional | Advanced URL handling | Latest | For more robust image downloading than urllib |
| font-hanken-grotesk | Optional | Better typography | Latest | Not used in current script but useful for text overlays |
| beautifulsoup4 | Optional | Web scraping | Latest | Potential future use for content gathering |
| font-* packages | Optional | Typography | Latest | Various fonts for text rendering |
| geocoder | Optional | Location services | Latest | Potential use for location-based displays |
| seaborn | Optional | Data visualization | Latest | Potential use for charts/graphs |
| wikiquotes | Optional | Content source | Latest | Potential quote display feature |

## Features Implementation Status

| Feature | Status | Priority | Notes |
|---------|--------|----------|-------|
| Basic image display | Implemented | High | Core functionality |
| URL image loading | Implemented | High | Core functionality |
| Local file loading | Implemented | High | Core functionality |
| Button controls | Implemented | High | Core functionality |
| Image scaling | Implemented | High | Core functionality |
| Image rotation | Implemented | High | Core functionality |
| Aspect ratio toggle | Implemented | High | Core functionality |
| Auto display detection | Implemented | High | Core functionality |
| Multi-display support | Implemented | Medium | Works with all Inky variants |
| Text overlay | Planned | Low | Add captions or text to images |
| Image filters | Planned | Low | B&W optimization, contrast enhancement |
| Slideshow mode | Planned | Low | Cycle through multiple images |
| Weather integration | Idea | Low | Display weather with images |
| RSS feed images | Idea | Low | Display images from news feeds |

## Project Goals

1. Create a simple, user-friendly image viewer for Inky displays
2. Support all Inky display variants
3. Provide intuitive button controls for image manipulation
4. Keep dependencies minimal for core functionality
5. Allow for easy extension and customization

## Development Roadmap

### Phase 1 (Current) - Core Image Viewer
- ✅ Basic image display functionality
- ✅ Button controls for manipulation
- ✅ Support for different display types

### Phase 2 - Enhanced Features
- ⬜ Add text overlay capabilities
- ⬜ Improve image processing for e-ink optimization
- ⬜ Add slideshow functionality

### Phase 3 - Integration Features
- ⬜ Weather data integration
- ⬜ RSS/news integration
- ⬜ Calendar integration

## Implementation Notes

Last updated: April 20, 2025

Current script uses only the essential dependencies (Inky, RPi.GPIO, PIL) to maintain simplicity and reliability. Optional dependencies will be integrated as new features are developed.

The button handling implementation was improved with a function factory pattern to avoid common lambda closure issues in event callbacks.
