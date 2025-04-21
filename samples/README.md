# Sample Images for InkyPie

This directory contains sample images for testing with the Inky displays. Sample images should be named according to the pattern `sample1.jpg`, `sample2.jpg`, etc.

## Using Sample Images

You can use these sample images with the Inky Image Viewer by specifying the sample number:

```bash
python ../inky_image_viewer.py --sample 1
```

## Recommended Image Properties

For best results with e-ink displays:

- **High Contrast**: E-ink displays work best with high-contrast images
- **Bold Elements**: Thin lines and subtle details may not display well
- **Appropriate Size**: Images will be automatically resized, but starting with dimensions close to your display size is ideal
- **Limited Color Palette**: For color displays, use bold, distinct colors

## Adding Your Own Samples

Feel free to add your own sample images to this directory. Just follow the naming convention:

- `sample1.jpg`
- `sample2.jpg`
- `sample3.jpg`
- etc.

These can be any common image format (JPG, PNG, GIF, BMP) and will be automatically processed for display.

## Included Samples

If you don't have any sample images, you can use URLs from the `sample_gallery.txt` file, which includes links to some example images:

```bash
python ../inky_image_viewer.py --gallery-file ../sample_gallery.txt
```
