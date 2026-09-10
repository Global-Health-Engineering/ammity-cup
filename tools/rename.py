"""The one file-name rule for everything copied into hardware/.

STEP and STL names are normalised mechanically so they read consistently
in a URL and a shell; NX .prt files are NOT renamed (NX part files can
reference each other by name, and a rename would break that), so this
rule is never applied to them. Digits are kept: some are piece indices
(twister_skin_mold_1 to _6) that a rule cannot tell apart from version
numbers.
"""
import os
import re

VARIANT_DIRS = {
    "Flower Low Cup": "flower-low",
    "Flower High Cup": "flower-high",
    "Twister Cup": "twister",
    "Umbrella Cup": "umbrella",
    "Drawstring Cup": "drawstring",
    "Duckbill Cup": "duckbill",
    "Balloon Cup": "balloon",
    "Extraction Valve": "extraction-valve",
    "Artificial Vagina": "artificial-vagina",
}

# Substring fixes for typos in the author's file names.
TYPO_FIXES = {"drawsting": "drawstring", "ousideleft": "outsideleft"}
EXTENSIONS = {".stp": ".step"}


def kebab(filename):
    stem, ext = os.path.splitext(filename)
    ext = EXTENSIONS.get(ext.lower(), ext.lower())
    out = []
    for token in re.split(r"[_\s-]+", stem.lower()):
        if not token or token == "m":
            continue
        for bad, good in TYPO_FIXES.items():
            token = token.replace(bad, good)
        out.append(token.replace("mold", "mould"))
    return "-".join(out) + ext
