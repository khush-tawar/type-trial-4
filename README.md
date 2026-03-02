# type-trial-4

# font-ai — AI Font Generator (Endangered Scripts)

## What This Project Does
This project trains an AI to understand the structure of letterforms across many 
typefaces, then uses that knowledge to morph between fonts and eventually generate 
new glyphs for scripts that are dying or underrepresented in digital typography.

The AI learns a "font manifold" — a mathematical space where similar fonts cluster 
together. Moving between two points in that space smoothly morphs one font into another.
This is based on the approach in "Learning a Manifold of Fonts" (UCL/SIGGRAPH 2014).

## Architecture
- **Model:** Variational Autoencoder (VAE) with convolutional encoder/decoder
- **Input:** 64x64 grayscale PNG images of individual glyphs
- **Latent space:** 32 dimensions (each font = 32 numbers = its address in font space)
- **Morphing:** Linear interpolation between two latent vectors
- **Future:** Vector (bezier) based training using SVG-VAE approach

## Project Structure
```
font-ai/
├── webapp/               # Browser-based font analyzer and morpher
├── data/
│   ├── raw_fonts/        # Downloaded .ttf/.otf files (not committed)
│   └── glyphs/
│       └── A/            # Extracted glyph PNGs, one per font
├── scripts/
│   └── extract_glyphs.py # Renders each font's glyph as PNG
├── notebooks/
│   └── 01_train_vae.ipynb # Full training pipeline
├── model/
│   ├── font_vae.pth       # Trained model weights (PyTorch)
│   └── font_vectors.json  # Latent vectors for all trained fonts
└── README.md
```

## Workflow
1. **VS Code** — write scripts, organize data, manage Git
2. **GitHub** — stores all code and model outputs
3. **Google Colab** — GPU training (clone repo → train → push results back)
4. **Webapp** — loads font_vectors.json, enables AI-powered morphing in browser

## Current Phase
Training on a single glyph (letter "A") across 80–150 Latin typefaces to prove 
the morphing concept before expanding to the target endangered script.

## Tech Stack
- Python, PyTorch (training)
- Pillow (glyph extraction)
- JavaScript, opentype.js (webapp)
- GitHub Pages (webapp hosting)

## Key Concepts
- **VAE:** Compresses images to 32 numbers, reconstructs them back. The compression 
  learns meaningful font structure, enabling smooth interpolation.
- **Convolution:** Inside the VAE encoder — detects strokes, curves, and letterform 
  structure. Deconvolution in the decoder reconstructs them.
- **SDF/MSDF:** Signed Distance Field representations (upgrade path after raster 
  training is working — improves edge quality for AI training).
- **Font manifold:** The learned latent space where similar fonts cluster. 
  Morphing = moving through this space.
```


