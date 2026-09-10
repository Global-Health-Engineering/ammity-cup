#!/usr/bin/env python3
"""Tessellate the STEP B-rep into per-solid binary STLs for the renders.

Run from the render venv (requirements-render.txt):
    .venv/bin/python tools/step_to_mesh.py

The cup geometry exists only as B-rep (Siemens NX parts and their STEP
exports); every STL the author supplied is a mould piece. Blender cannot
read STEP, so this script meshes each STEP with OpenCascade into
build/meshes/<slug>/<step-stem>/solid-<i>.stl, one file per solid, plus an
index.json with each solid's bounding box and volume. tools/parts.py
refers to solids by that index. Nothing here is committed: build/ is
git-ignored and every file regenerates from hardware/.

Solid order is the order OpenCascade's explorer returns them in, which is
the STEP file's own order and is stable across runs.

OCP 8 notes: static methods lost their `_s` suffix (hence `_static`), and
Bnd_Box.Get() cannot convert its return type, so bounding boxes are taken
from the mesh nodes instead.
"""
import glob
import json
import os
import struct
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_ROOT = os.path.join(ROOT, "build", "meshes")
# 0.02 mm chordal deviation keeps the thinnest petals and strings smooth in
# a 2000 px render; the heaviest part (flower-high) lands near 66 k
# triangles, which render_parts.py decimates for the web copy.
LINEAR_DEFLECTION_MM = 0.02
ANGULAR_DEFLECTION_RAD = 0.2


def _static(cls, name):
    return getattr(cls, name + "_s", None) or getattr(cls, name)


def write_stl(path, tris):
    """Binary STL; each normal is the unit cross product of the triangle's
    own winding (zero for degenerate triangles)."""
    tris = np.asarray(tris, dtype=np.float64)
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    length = np.linalg.norm(n, axis=1, keepdims=True)
    n = np.divide(n, length, out=np.zeros_like(n), where=length > 0)
    rec = np.zeros(len(tris), dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    rec["n"], rec["v"] = n, tris
    with open(path, "wb") as f:
        f.write(b"binary STL written by tools/step_to_mesh.py".ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        f.write(rec.tobytes())


def _read_shape(step_path):
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader
    reader = STEPControl_Reader()
    if reader.ReadFile(step_path) != IFSelect_RetDone:
        raise ValueError(f"{step_path}: could not be read as STEP")
    reader.TransferRoots()
    return reader.OneShape()


def _solid_triangles(solid):
    from OCP.BRep import BRep_Tool
    from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS
    chunks = []
    faces = TopExp_Explorer(solid, TopAbs_FACE)
    while faces.More():
        face = _static(TopoDS, "Face")(faces.Current())
        loc = TopLoc_Location()
        tri = _static(BRep_Tool, "Triangulation")(face, loc)
        if tri is not None:
            trsf = loc.Transformation()
            nodes = np.array([[p.X(), p.Y(), p.Z()] for p in
                              (tri.Node(i).Transformed(trsf) for i in range(1, tri.NbNodes() + 1))])
            idx = np.array([tri.Triangle(i).Get() for i in range(1, tri.NbTriangles() + 1)]) - 1
            if face.Orientation() == TopAbs_REVERSED:
                idx = idx[:, [0, 2, 1]]
            chunks.append(nodes[idx])
        faces.Next()
    return np.concatenate(chunks)


def mesh_step(step_path, out_dir):
    from OCP.BRepGProp import BRepGProp
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.GProp import GProp_GProps
    from OCP.TopAbs import TopAbs_SOLID
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS
    shape = _read_shape(step_path)
    BRepMesh_IncrementalMesh(shape, LINEAR_DEFLECTION_MM, False, ANGULAR_DEFLECTION_RAD, True)
    os.makedirs(out_dir, exist_ok=True)
    records = []
    solids = TopExp_Explorer(shape, TopAbs_SOLID)
    while solids.More():
        solid = _static(TopoDS, "Solid")(solids.Current())
        tris = _solid_triangles(solid)
        props = GProp_GProps()
        _static(BRepGProp, "VolumeProperties")(solid, props)
        i = len(records)
        name = f"solid-{i}.stl"
        write_stl(os.path.join(out_dir, name), tris)
        pts = tris.reshape(-1, 3)
        records.append({
            "index": i, "file": name, "triangles": int(len(tris)),
            "bbox_min": [round(float(x), 4) for x in pts.min(0)],
            "bbox_max": [round(float(x), 4) for x in pts.max(0)],
            "volume_cm3": round(props.Mass() / 1000.0, 4),
        })
        solids.Next()
    if not records:
        raise ValueError(f"{step_path}: no solids found")
    return records


def main(argv=None):
    steps = sorted(glob.glob(os.path.join(ROOT, "hardware", "*", "step", "*.step")))
    if not steps:
        print("step_to_mesh: no STEP files under hardware/*/step/", file=sys.stderr)
        return 1
    for step in steps:
        slug = step.split(os.sep)[-3]
        stem = os.path.splitext(os.path.basename(step))[0]
        out = os.path.join(OUT_ROOT, slug, stem)
        records = mesh_step(step, out)
        with open(os.path.join(out, "index.json"), "w") as f:
            json.dump({"step": os.path.relpath(step, ROOT), "solids": records}, f, indent=2)
        print(f"  {slug}/{stem}: {len(records)} solid(s), "
              f"{sum(r['triangles'] for r in records):,} tris")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
