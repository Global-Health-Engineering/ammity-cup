#!/usr/bin/env python3
"""Release gate: this repository must contain only material that can be
published.

Never tracked here: the thesis itself (not released, D4), the flight
questionnaires and the training slides (they name the analogue astronauts
and carry a personal email address), NX/STEP translation logs (they embed
the author's local Windows path), planning content, intermediate meshes,
raw video, and any certification artwork the project is not entitled to
display (the project is not certified, D8).

Only paths Git tracks are checked (`git ls-files`), so the staging
directory incoming/, which is git-ignored, never trips it; anything
`git add -f`'d against .gitignore will.

Usage:  python3 tools/verify_scope.py
   or:  python3 -m tools.verify_scope
"""
import fnmatch
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Case-insensitive substrings anywhere in the path -> reason.
BANNED_SUBSTRINGS = {
    "thesis": "the thesis is not part of this release",
    "questionaire": "questionnaires name participants; ship data/flight-questionnaire.csv instead",
    "questionnaire": "questionnaires name participants; ship data/flight-questionnaire.csv instead",
    "training slides": "the slides carry a personal email address",
    "certification-mark": "the project is not entitled to display this certification mark",
    "oshwa": "the project is not entitled to display this certification mark",
}

BANNED_PATH_PREFIXES = [
    "incoming",
    "build",
    ".superpowers",
    "docs/superpowers",
]

BANNED_EXTENSIONS = [
    ".pptx", ".ppt", ".xlsx", ".docx",
    ".log",
    ".mov", ".mp4", ".heic",
    ".blend", ".blend1",
]

# Reviewed exceptions to BANNED_SUBSTRINGS: the anonymised questionnaire
# table (participants P1-P3, no names) is the intended published form.
ALLOWED_PATH_EXCEPTIONS = {
    "data/flight-questionnaire.csv",
}


def _matches_path_prefix(posix_path, rule):
    lowered = posix_path.lower()
    rule = rule.lower().rstrip("/")
    return (
        lowered == rule
        or lowered.startswith(rule + "/")
        or ("/" + rule + "/") in lowered
    )


def offending_reason(path):
    """Return a human-readable reason `path` is out of scope, or None."""
    posix_path = path.replace(os.sep, "/")
    lowered = posix_path.lower()

    if posix_path in ALLOWED_PATH_EXCEPTIONS:
        return None

    for needle in BANNED_SUBSTRINGS:
        if needle in lowered:
            return f"contains {needle!r}: {BANNED_SUBSTRINGS[needle]}"

    for rule in BANNED_PATH_PREFIXES:
        if _matches_path_prefix(posix_path, rule):
            return f"is under {rule!r}, excluded from the release"

    _, ext = os.path.splitext(posix_path)
    for banned in BANNED_EXTENSIONS:
        if fnmatch.fnmatch(ext.lower(), banned):
            return f"has extension {ext!r}, excluded file type"

    return None


def tracked_files():
    """Return the list of paths Git currently tracks, repo-relative."""
    out = subprocess.run(
        ["git", "ls-files", "-z"],
        capture_output=True,
        check=True,
    ).stdout
    return [p for p in out.decode("utf-8", "surrogateescape").split("\0") if p]


def main(paths=None):
    files = paths if paths is not None else tracked_files()
    offenders = []
    for path in sorted(files):
        reason = offending_reason(path)
        if reason:
            offenders.append((path, reason))

    if not offenders:
        print(f"verify_scope: {len(files)} tracked files, 0 out of scope")
        return 0

    print(f"verify_scope: {len(offenders)} out-of-scope file(s) found:\n")
    for path, reason in offenders:
        print(f"  FAIL  {path}\n        {reason}")
    print(
        f"\n{len(offenders)} offending file(s) must be removed from the "
        f"index (git rm --cached) before this repository can ship."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
