#!/usr/bin/env python3
"""Release gate: no personal data in anything this repository ships.

Three things are checked in every tracked text file and in the built site:

  * participant names from the parabolic-flight questionnaires. Only
    SHA-256 hashes of the lower-cased names (full name, given name,
    family name) are stored, in tools/privacy_hashes.txt, so the gate
    does not itself publish what it protects. Every 1-, 2- and 3-word
    sequence of the scanned text is hashed and looked up. Caveat: a
    common given name hashed alone is reversible by dictionary, which is
    why the list exists to block leaks, not to keep the names secret.
  * Windows user-profile paths (e.g. C:/Users/<name>/...), which NX
    writes into STEP translation logs.
  * email addresses.

Usage:  python3 tools/verify_privacy.py                 (tracked text files)
   or:  python3 tools/verify_privacy.py "site/dist/**/*.html"
"""
import glob
import hashlib
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_HASHES = os.path.join(ROOT, "tools", "privacy_hashes.txt")
TEXT_SUFFIXES = (".md", ".astro", ".json", ".csv", ".txt", ".js", ".mjs",
                 ".cff", ".yml", ".yaml", ".html", ".css", ".py", ".svg")
MAX_NGRAM = 3

_WORD = re.compile(r"[^\W\d_]+")
_WINDOWS_PATH = re.compile(r"[a-z]:\\{1,2}users\\{1,2}", re.IGNORECASE)
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# Institutional contact addresses that are meant to be public (the site
# footer links the group's address, as 3DPLAM's does). Personal addresses
# are never added here.
ALLOWED_EMAILS = {"ghe" + "@" + "mavt.ethz.ch"}


def name_hash(text):
    tokens = _WORD.findall(text.lower())
    return hashlib.sha256(" ".join(tokens).encode("utf-8")).hexdigest()


def load_hashes(path):
    with open(path, encoding="utf-8") as f:
        return {l.strip() for l in f if l.strip() and not l.startswith("#")}


def scan_text(text, hashes):
    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if _WINDOWS_PATH.search(line):
            hits.append((line_no, "windows-path"))
        if any(m.group(0).lower() not in ALLOWED_EMAILS for m in _EMAIL.finditer(line)):
            hits.append((line_no, "email"))
        if hashes:
            words = _WORD.findall(line.lower())
            for n in range(1, MAX_NGRAM + 1):
                for i in range(len(words) - n + 1):
                    digest = hashlib.sha256(" ".join(words[i:i + n]).encode()).hexdigest()
                    if digest in hashes:
                        hits.append((line_no, "name"))
    return hits


def default_files():
    out = subprocess.run(["git", "ls-files", "-z"], capture_output=True,
                         check=True, cwd=ROOT).stdout.decode()
    return [os.path.join(ROOT, p) for p in out.split("\0")
            if p and p.lower().endswith(TEXT_SUFFIXES)
            and p != "tools/privacy_hashes.txt"]


def main(patterns=None, hashes_path=DEFAULT_HASHES):
    # Fail closed: without a usable hash list the name check would
    # silently do nothing (scan_text skips n-grams when hashes is empty)
    # and a leak would be indistinguishable from a clean run.
    try:
        hashes = load_hashes(hashes_path)
    except OSError:
        hashes = None
    if not hashes:
        print(f"verify_privacy: no participant-name hashes loaded from "
              f"{hashes_path}; the name check cannot run. Regenerate "
              f"tools/privacy_hashes.txt (see Task docs) before shipping.",
              file=sys.stderr)
        return 1
    if patterns:
        files = sorted({f for p in patterns for f in glob.glob(p, recursive=True)
                        if os.path.isfile(f) and f.lower().endswith(TEXT_SUFFIXES)})
    else:
        files = default_files()
    if not files:
        print("verify_privacy: no files matched", file=sys.stderr)
        return 1
    failed = 0
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line_no, kind in scan_text(f.read(), hashes):
                failed += 1
                # Never echo the matching text: that would print the name.
                print(f"  FAIL  {os.path.relpath(path, ROOT)}:{line_no}  {kind}")
    if failed:
        print(f"\n{failed} personal-data hit(s). Remove or anonymise them (P1-P3).")
        return 1
    print(f"verify_privacy: {len(files)} file(s) scanned, 0 hits")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
