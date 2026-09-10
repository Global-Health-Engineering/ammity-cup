#!/usr/bin/env python3
"""Release gate: the copy must not claim more than the evidence supports.

The SpaceCup was bench-tested at 1 G and flown for a handful of ~6 s
reduced-gravity windows, with no measured volumes in flight. It is a
research prototype. Copy that calls it certified, approved, clinically
tested, safe for human use or leak-proof overstates that, and so does any
OSHWA reference (the project is not certified). This gate fails the build
if such phrasing reaches the docs or the built site.

Usage:  python3 tools/verify_copy.py                    (scans the defaults)
   or:  python3 tools/verify_copy.py "README.md" "docs/**/*.md"
   or:  python3 -m tools.verify_copy "site/dist/**/*.html"
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BANNED_PHRASES = [
    "fda-approved", "fda approved", "ce-marked", "ce marked",
    "clinically tested", "clinically proven", "clinically validated",
    "medically approved", "safe for human use", "safe to use",
    "leak-proof", "leakproof", "space-qualified", "flight-qualified",
    "oshwa", "certified medical device",
]

# The one sanctioned use of "certified medical device" is its negation,
# the disclaimer the spec requires. A hit on that phrase is ignored only for
# the exact patterns: "not a certified medical device" or "does not make <1-4 words> a certified medical device".
_NEGATED = re.compile(r"(?:\bnot an?|\bdoes not make(?:\s+[\w-]+){1,4}\s+an?)\s+certified medical device")

# Scanned when no paths are given on the command line: every markdown page
# plus the Astro site *source* (components, layouts, and the copy-holding
# site.json). This catches banned phrasing at the point someone would
# actually type it. It is deliberately not sufficient on its own; see
# tools/README.md and .github/workflows/verify.yml, where a second
# invocation scans the *built* site/dist/**/*.html, because the built HTML
# is what actually ships and could in principle differ from any single
# source file (e.g. text assembled across a template and a data file).
DEFAULT_PATTERNS = [
    "README.md",
    "docs/**/*.md",
    "site/src/**/*.astro",
    "site/src/**/*.md",
    "site/src/**/*.json",
]

TEXT_SUFFIXES = (".md", ".astro", ".json", ".html", ".mdx", ".txt", ".css", ".js")


def find_files(patterns):
    files = set()
    for pattern in patterns:
        for match in glob.glob(pattern, recursive=True):
            if os.path.isfile(match) and match.lower().endswith(TEXT_SUFFIXES):
                files.add(match)
    return sorted(files)


def scan_file(path):
    """Return a list of (line_no, phrase, line_text) hits in `path`."""
    hits = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, start=1):
            lowered = line.lower()
            for phrase in BANNED_PHRASES:
                if phrase not in lowered:
                    continue
                if phrase == "certified medical device" and _NEGATED.search(lowered):
                    continue
                hits.append((line_no, phrase, line.strip()))
    return hits


def main(patterns=None):
    patterns = patterns if patterns else DEFAULT_PATTERNS
    files = find_files(patterns)
    if not files:
        print("verify_copy: no files matched", file=sys.stderr)
        return 1

    total_hits = 0
    for path in files:
        for line_no, phrase, line_text in scan_file(path):
            total_hits += 1
            print(f"  FAIL  {path}:{line_no}  {phrase!r}\n        {line_text}")

    if total_hits:
        print(
            f"\n{total_hits} banned phrase occurrence(s) in {len(files)} "
            f"file(s) scanned. The SpaceCup is a research prototype tested on the bench and in short parabolic-flight windows; reword without claims of certification, approval, clinical testing, safety for human use or leak-proofness."
        )
        return 1

    print(f"verify_copy: {len(files)} file(s) scanned, 0 banned phrases")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
