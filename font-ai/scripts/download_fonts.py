"""
download_fonts.py  —  Download ~100 popular Google Fonts (.ttf) into data/raw_fonts/

Downloads fonts from the google/fonts GitHub repository, which hosts
actual .ttf files (not web-only formats like EOT or WOFF2).

Usage (from the font-ai/ directory):
    python scripts/download_fonts.py

Requirements:
    pip install requests
"""

import os
import sys
import json
import re
import requests
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TARGET_COUNT = 100  # How many fonts to download

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAW_FONTS_DIR = PROJECT_ROOT / "data" / "raw_fonts"

# (family_name, github_folder, filename) — google/fonts GitHub repo layout
# Folder is under ofl/ or apache/ in google/fonts repo on GitHub.
# We map each font to its known path in the repo.
FONT_ENTRIES = [
    # --- Already present (will be skipped) ---
    ("Roboto", "apache/roboto", "Roboto-Regular.ttf"),
    ("OpenSans", "apache/opensans", "OpenSans%5Bwdth%2Cwght%5D.ttf"),  # variable
    ("Lora", "ofl/lora", "Lora%5Bwght%5D.ttf"),
    ("Merriweather", "ofl/merriweather", "Merriweather-Regular.ttf"),
    ("PlayfairDisplay", "ofl/playfairdisplay", "PlayfairDisplay%5Bwght%5D.ttf"),
    # --- New fonts ---
    ("Lato", "ofl/lato", "Lato-Regular.ttf"),
    ("Montserrat", "ofl/montserrat", "Montserrat%5Bwght%5D.ttf"),
    ("Oswald", "ofl/oswald", "Oswald%5Bwght%5D.ttf"),
    ("Raleway", "ofl/raleway", "Raleway%5Bwght%5D.ttf"),
    ("Poppins", "ofl/poppins", "Poppins-Regular.ttf"),
    ("NotoSans", "ofl/notosans", "NotoSans%5Bwdth%2Cwght%5D.ttf"),
    ("Ubuntu", "ufl/ubuntu", "Ubuntu-Regular.ttf"),
    ("PTSans", "ofl/ptsans", "PTSans-Regular.ttf"),
    ("RobotoCondensed", "apache/robotocondensed", "RobotoCondensed%5Bwght%5D.ttf"),
    ("Nunito", "ofl/nunito", "Nunito%5Bwght%5D.ttf"),
    ("RobotoSlab", "apache/robotoslab", "RobotoSlab%5Bwght%5D.ttf"),
    ("Inter", "ofl/inter", "Inter%5Bopsz%2Cwght%5D.ttf"),
    ("Mukta", "ofl/mukta", "Mukta-Regular.ttf"),
    ("Rubik", "ofl/rubik", "Rubik%5Bwght%5D.ttf"),
    ("WorkSans", "ofl/worksans", "WorkSans%5Bwght%5D.ttf"),
    ("NunitoSans", "ofl/nunitosans", "NunitoSans%5Bopsz%2Cwght%5D.ttf"),
    ("FiraSans", "ofl/firasans", "FiraSans-Regular.ttf"),
    ("Quicksand", "ofl/quicksand", "Quicksand%5Bwght%5D.ttf"),
    ("Barlow", "ofl/barlow", "Barlow-Regular.ttf"),
    ("Mulish", "ofl/mulish", "Mulish%5Bwght%5D.ttf"),
    ("Heebo", "ofl/heebo", "Heebo%5Bwght%5D.ttf"),
    ("Inconsolata", "ofl/inconsolata", "Inconsolata%5Bwdth%2Cwght%5D.ttf"),
    ("TitilliumWeb", "ofl/titilliumweb", "TitilliumWeb-Regular.ttf"),
    ("Karla", "ofl/karla", "Karla%5Bwght%5D.ttf"),
    ("DMSans", "ofl/dmsans", "DMSans%5Bopsz%2Cwght%5D.ttf"),
    ("Manrope", "ofl/manrope", "Manrope%5Bwght%5D.ttf"),
    ("LibreFranklin", "ofl/librefranklin", "LibreFranklin%5Bwght%5D.ttf"),
    ("Dosis", "ofl/dosis", "Dosis%5Bwght%5D.ttf"),
    ("JosefinSans", "ofl/josefinsans", "JosefinSans%5Bwght%5D.ttf"),
    ("Arimo", "apache/arimo", "Arimo%5Bwght%5D.ttf"),
    ("Cabin", "ofl/cabin", "Cabin%5Bwdth%2Cwght%5D.ttf"),
    ("Anton", "ofl/anton", "Anton-Regular.ttf"),
    ("Bitter", "ofl/bitter", "Bitter%5Bwght%5D.ttf"),
    ("LibreBaskerville", "ofl/librebaskerville", "LibreBaskerville-Regular.ttf"),
    ("Abel", "ofl/abel", "Abel-Regular.ttf"),
    ("Lobster", "ofl/lobster", "Lobster-Regular.ttf"),
    ("DancingScript", "ofl/dancingscript", "DancingScript%5Bwght%5D.ttf"),
    ("Pacifico", "ofl/pacifico", "Pacifico-Regular.ttf"),
    ("IndieFlower", "ofl/indieflower", "IndieFlower-Regular.ttf"),
    ("EBGaramond", "ofl/ebgaramond", "EBGaramond%5Bwght%5D.ttf"),
    ("Exo2", "ofl/exo2", "Exo2%5Bwght%5D.ttf"),
    ("Signika", "ofl/signika", "Signika%5BFILL%2Cwght%5D.ttf"),
    ("Hind", "ofl/hind", "Hind-Regular.ttf"),
    ("Archivo", "ofl/archivo", "Archivo%5Bwdth%2Cwght%5D.ttf"),
    ("VarelaRound", "ofl/varelaround", "VarelaRound-Regular.ttf"),
    ("Overpass", "ofl/overpass", "Overpass%5Bwght%5D.ttf"),
    ("Cairo", "ofl/cairo", "Cairo%5Bslnt%2Cwght%5D.ttf"),
    ("Asap", "ofl/asap", "Asap%5Bwdth%2Cwght%5D.ttf"),
    ("IBMPlexSans", "ofl/ibmplexsans", "IBMPlexSans-Regular.ttf"),
    ("CrimsonText", "ofl/crimsontext", "CrimsonText-Regular.ttf"),
    ("YanoneKaffeesatz", "ofl/yanonekaffeesatz", "YanoneKaffeesatz%5Bwght%5D.ttf"),
    ("Catamaran", "ofl/catamaran", "Catamaran%5Bwght%5D.ttf"),
    ("Comfortaa", "ofl/comfortaa", "Comfortaa%5Bwght%5D.ttf"),
    ("SourceCodePro", "ofl/sourcecodepro", "SourceCodePro%5Bwght%5D.ttf"),
    ("Prompt", "ofl/prompt", "Prompt-Regular.ttf"),
    ("Questrial", "ofl/questrial", "Questrial-Regular.ttf"),
    ("CormorantGaramond", "ofl/cormorantgaramond", "CormorantGaramond-Regular.ttf"),
    ("SpaceGrotesk", "ofl/spacegrotesk", "SpaceGrotesk%5Bwght%5D.ttf"),
    ("Kanit", "ofl/kanit", "Kanit-Regular.ttf"),
    ("BarlowCondensed", "ofl/barlowcondensed", "BarlowCondensed-Regular.ttf"),
    ("Sarabun", "ofl/sarabun", "Sarabun-Regular.ttf"),
    ("Teko", "ofl/teko", "Teko%5Bwght%5D.ttf"),
    ("FjallaOne", "ofl/fjallaone", "FjallaOne-Regular.ttf"),
    ("BebasNeue", "ofl/bebasneue", "BebasNeue-Regular.ttf"),
    ("MavenPro", "ofl/mavenpro", "MavenPro%5Bwght%5D.ttf"),
    ("NanumGothic", "ofl/nanumgothic", "NanumGothic-Regular.ttf"),
    ("Acme", "ofl/acme", "Acme-Regular.ttf"),
    ("Righteous", "ofl/righteous", "Righteous-Regular.ttf"),
    ("SignikaNegative", "ofl/signikanegative", "SignikaNegative%5Bwght%5D.ttf"),
    ("Assistant", "ofl/assistant", "Assistant%5Bwght%5D.ttf"),
    ("Alegreya", "ofl/alegreya", "Alegreya%5Bwght%5D.ttf"),
    ("Cardo", "ofl/cardo", "Cardo-Regular.ttf"),
    ("Oxygen", "ofl/oxygen", "Oxygen-Regular.ttf"),
    ("Rajdhani", "ofl/rajdhani", "Rajdhani-Regular.ttf"),
    ("RussoOne", "ofl/russoone", "RussoOne-Regular.ttf"),
    ("PatuaOne", "ofl/patuaone", "PatuaOne-Regular.ttf"),
    ("Vollkorn", "ofl/vollkorn", "Vollkorn%5Bwght%5D.ttf"),
    ("ShadowsIntoLight", "ofl/shadowsintolight", "ShadowsIntoLight-Regular.ttf"),
    ("AmaticSC", "ofl/amaticsc", "AmaticSC-Regular.ttf"),
    ("Satisfy", "ofl/satisfy", "Satisfy-Regular.ttf"),
    ("Courgette", "ofl/courgette", "Courgette-Regular.ttf"),
    ("GreatVibes", "ofl/greatvibes", "GreatVibes-Regular.ttf"),
    ("AlfaSlabOne", "ofl/alfaslabone", "AlfaSlabOne-Regular.ttf"),
    ("Sacramento", "ofl/sacramento", "Sacramento-Regular.ttf"),
    ("ArchitectsDaughter", "ofl/architectsdaughter", "ArchitectsDaughter-Regular.ttf"),
    ("PermanentMarker", "ofl/permanentmarker", "PermanentMarker-Regular.ttf"),
    ("Caveat", "ofl/caveat", "Caveat%5Bwght%5D.ttf"),
    ("Yellowtail", "ofl/yellowtail", "Yellowtail-Regular.ttf"),
    ("Cookie", "ofl/cookie", "Cookie-Regular.ttf"),
    ("KaushanScript", "ofl/kaushanscript", "KaushanScript-Regular.ttf"),
    ("GloriaHallelujah", "ofl/gloriahallelujah", "GloriaHallelujah-Regular.ttf"),
    ("Bangers", "ofl/bangers", "Bangers-Regular.ttf"),
    ("PressStart2P", "ofl/pressstart2p", "PressStart2P-Regular.ttf"),
    ("SpecialElite", "ofl/specialelite", "SpecialElite-Regular.ttf"),
    ("AbrilFatface", "ofl/abrilfatface", "AbrilFatface-Regular.ttf"),
    ("Cinzel", "ofl/cinzel", "Cinzel%5Bwght%5D.ttf"),
    ("Philosopher", "ofl/philosopher", "Philosopher-Regular.ttf"),
    ("Spectral", "ofl/spectral", "Spectral-Regular.ttf"),
    ("ZillaSlab", "ofl/zillaslab", "ZillaSlab-Regular.ttf"),
    ("Arvo", "ofl/arvo", "Arvo-Regular.ttf"),
    ("NotoSerif", "ofl/notoserif", "NotoSerif%5Bwdth%2Cwght%5D.ttf"),
    ("PTSerif", "ofl/ptserif", "PTSerif-Regular.ttf"),
    ("Rokkitt", "ofl/rokkitt", "Rokkitt%5Bwght%5D.ttf"),
    ("AlegreyaSans", "ofl/alegreyasans", "AlegreyaSans-Regular.ttf"),
    ("Jost", "ofl/jost", "Jost%5Bwght%5D.ttf"),
    ("Sora", "ofl/sora", "Sora%5Bwght%5D.ttf"),
    ("RedHatDisplay", "ofl/redhatdisplay", "RedHatDisplay%5Bwght%5D.ttf"),
    ("Outfit", "ofl/outfit", "Outfit%5Bwght%5D.ttf"),
    ("Lexend", "ofl/lexend", "Lexend%5Bwght%5D.ttf"),
    ("PlusJakartaSans", "ofl/plusjakartasans", "PlusJakartaSans%5Bwght%5D.ttf"),
    ("Figtree", "ofl/figtree", "Figtree%5Bwght%5D.ttf"),
]

GITHUB_RAW_BASE = "https://github.com/google/fonts/raw/main"


def download_font(name: str, folder: str, filename: str, out_dir: Path) -> bool:
    """
    Download a font .ttf from the google/fonts GitHub repo.
    Returns True on success, False on failure.
    """
    out_path = out_dir / f"{name}.ttf"

    # Skip if already downloaded
    if out_path.exists():
        return True

    url = f"{GITHUB_RAW_BASE}/{folder}/{filename}"
    try:
        resp = requests.get(url, timeout=30, allow_redirects=True)
        resp.raise_for_status()
        out_path.write_bytes(resp.content)
        return True
    except Exception as e:
        print(f"  ✗ {name} — {e}")
        return False


def main():
    RAW_FONTS_DIR.mkdir(parents=True, exist_ok=True)

    # Count existing fonts
    existing = set(p.stem for p in RAW_FONTS_DIR.iterdir()
                   if p.suffix.lower() in (".ttf", ".otf"))
    print(f"Already have {len(existing)} fonts in {RAW_FONTS_DIR}")

    succeeded = len(existing)
    attempted = 0

    for name, folder, filename in FONT_ENTRIES:
        if name in existing:
            continue

        attempted += 1
        print(f"  [{succeeded+1}/{TARGET_COUNT}] Downloading {name}...")
        if download_font(name, folder, filename, RAW_FONTS_DIR):
            succeeded += 1
            existing.add(name)
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} — skipped")

        if succeeded >= TARGET_COUNT:
            break

    print(f"\n{'='*50}")
    print(f"Done! {succeeded} fonts now in {RAW_FONTS_DIR}")
    print(f"(Downloaded {attempted} new fonts this run)")


if __name__ == "__main__":
    main()
