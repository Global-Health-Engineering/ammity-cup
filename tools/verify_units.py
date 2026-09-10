#!/usr/bin/env python3
"""Release gate: every shipped STL must be in millimetres.

STL has no unit header; a mould exported in metres would import 1000x too small. This check fails the build rather than shipping unprintable geometry.

Usage:  python3 tools/verify_units.py "hardware/*/mould-stl/*.stl"
   or:  python3 -m tools.verify_units "hardware/*/mould-stl/*.stl"
"""
import glob
import os
import sys

# Make the repository root importable so this file works both as a script
# (python3 tools/verify_units.py) and as a module (python3 -m tools.…).
# Without this, direct script invocation fails with ModuleNotFoundError
# because tools/ (not the repo root) is what lands on sys.path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.stl_units import read_stl, max_dimension  # noqa: E402

MIN_MM = 10.0
MAX_MM = 500.0


def check_file(path):
    """Return (ok, max_dimension, message) for one STL.

    Never raises: an unreadable file is a gate failure like any other, so
    that one bad file cannot abort the batch and hide the state of the
    files after it.
    """
    try:
        triangles, _ = read_stl(path)
        dim = max_dimension(triangles)
    except Exception as exc:
        return False, 0.0, f"could not be read as a binary STL: {exc}"
    if dim < MIN_MM:
        return False, dim, (
            f"{dim:.4f} mm is below {MIN_MM} mm; this looks like a file "
            f"exported in metres. Re-export with Units = Millimeter, or "
            f"rescale x1000."
        )
    if dim > MAX_MM:
        return False, dim, (
            f"{dim:.1f} mm exceeds {MAX_MM} mm; check the export units."
        )
    return True, dim, "ok"


def main(paths):
    files = sorted({f for p in paths for f in glob.glob(p)})
    if not files:
        print("verify_units: no STL files matched", file=sys.stderr)
        return 1
    failed = 0
    for path in files:
        ok, dim, msg = check_file(path)
        if ok:
            print(f"  PASS  {dim:8.2f} mm  {path}")
        else:
            print(f"  FAIL  {dim:8.4f} mm  {path}\n        {msg}")
            failed += 1
    print(f"\n{len(files) - failed}/{len(files)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["hardware/*/mould-stl/*.stl"]))
