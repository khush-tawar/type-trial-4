"""
encode_glyphs.py  —  Encode all glyph images through the trained VAE
and save the latent vectors to font_vectors.json.

Usage (from the repo root):
    python font-ai/scripts/encode_glyphs.py

Requirements:
    pip install torch Pillow
"""

import json
import sys
from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent          # font-ai/
REPO_ROOT = PROJECT_ROOT.parent           # repo root
GLYPHS_DIR = PROJECT_ROOT / "data" / "glyphs" / "A"
MODEL_PATH = REPO_ROOT / "font_vae.pth"
OUTPUT_PATH = REPO_ROOT / "font_vectors.json"

# ---------------------------------------------------------------------------
# VAE model definition (must match the Colab training code)
# ---------------------------------------------------------------------------
IMG_SIZE = 64  # The model was trained on 64×64 images
LATENT_DIM = 32


class FontVAE(nn.Module):
    def __init__(self, latent_dim=LATENT_DIM):
        super().__init__()
        # Encoder: 1×64×64 → 256×4×4
        self.encoder = nn.Sequential(
            nn.Conv2d(1, 32, 4, stride=2, padding=1),   # → 32×32×32
            nn.ReLU(),
            nn.Conv2d(32, 64, 4, stride=2, padding=1),  # → 64×16×16
            nn.ReLU(),
            nn.Conv2d(64, 128, 4, stride=2, padding=1), # → 128×8×8
            nn.ReLU(),
            nn.Conv2d(128, 256, 4, stride=2, padding=1),# → 256×4×4
            nn.ReLU(),
        )
        self.fc_mu = nn.Linear(256 * 4 * 4, latent_dim)
        self.fc_logvar = nn.Linear(256 * 4 * 4, latent_dim)

        # Decoder (not needed for encoding, but required to load weights)
        self.decoder_input = nn.Linear(latent_dim, 256 * 4 * 4)
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(256, 128, 4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(128, 64, 4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 32, 4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(32, 1, 4, stride=2, padding=1),
            nn.Sigmoid(),
        )

    def encode(self, x):
        h = self.encoder(x)
        h = h.view(h.size(0), -1)
        return self.fc_mu(h), self.fc_logvar(h)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    device = torch.device("cpu")

    # Load model
    print(f"Loading model from {MODEL_PATH}")
    model = FontVAE(LATENT_DIM)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device, weights_only=False))
    model.eval()

    # Gather all glyph PNGs
    glyph_files = sorted(GLYPHS_DIR.glob("*.png"))
    if not glyph_files:
        print(f"No glyph images found in {GLYPHS_DIR}")
        sys.exit(1)

    print(f"Encoding {len(glyph_files)} glyph images...\n")

    vectors = {}
    for glyph_path in glyph_files:
        # Load, resize to 64×64, normalise to [0, 1]
        img = Image.open(glyph_path).convert("L").resize((IMG_SIZE, IMG_SIZE))
        tensor = torch.tensor(list(img.getdata()), dtype=torch.float32)
        tensor = tensor.view(1, 1, IMG_SIZE, IMG_SIZE) / 255.0

        with torch.no_grad():
            mu, _ = model.encode(tensor)

        vectors[glyph_path.name] = mu.squeeze().tolist()
        print(f"  ✓ {glyph_path.name}")

    # Save
    with open(OUTPUT_PATH, "w") as f:
        json.dump(vectors, f)

    print(f"\n{'='*50}")
    print(f"Saved {len(vectors)} latent vectors to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
