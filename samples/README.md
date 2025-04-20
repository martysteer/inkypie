# Sample Images for InkyPie

This directory contains sample images optimized for Inky displays.

## Available Samples

1. **sample1.svg** - Basic InkyPie logo with red and black elements
   - Size: 400×300 pixels
   - Colors: Black, red, white
   - Good test for multi-color Inky displays

2. **sample2_bw.svg** - E-ink optimized high contrast sample
   - Size: 400×300 pixels  
   - Colors: Black and white only
   - Features grid pattern and concentric circles
   - Perfect for testing contrast and detail rendering

## Usage

Run the image viewer with these samples:

```bash
# Display the InkyPie logo
python3 ../inky_image_viewer.py --url samples/sample1.svg

# Display the black and white optimized sample
python3 ../inky_image_viewer.py --url samples/sample2_bw.svg
```

## Display Optimization Tips

For best results with e-ink displays:

1. **High Contrast**: Use stark black and white elements when possible
2. **Bold Lines**: Thin lines may not render well on e-ink
3. **Limited Colors**: Only use colors supported by your display
4. **Avoid Gradients**: E-ink displays can't show smooth gradients
5. **Optimize Text**: Use larger, bold fonts for better readability
6. **Consider Dithering**: When converting color images

## Creating Your Own Samples

SVG files work well because they're scalable and can be easily modified. Create your own samples using vector graphics software like Inkscape or Adobe Illustrator.

For bitmap images, PNG format is recommended. Consider these resolutions for different Inky displays:

- **Inky pHAT**: 212×104 or 250×122 pixels
- **Inky wHAT**: 400×300 pixels
- **Inky Impression 4"**: 640×400 pixels
- **Inky Impression 5.7"**: 600×448 pixels
- **Inky Impression 7.3"**: 800×480 pixels
