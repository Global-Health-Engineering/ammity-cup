import json, os
import numpy as np
import pytest
from tools.stl_units import read_stl
from tools.step_to_mesh import write_stl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ocp = pytest.importorskip  # alias for readability below

def cube_tris(size=10.0):
    v = np.array([[x, y, z] for x in (0, size) for y in (0, size) for z in (0, size)], float)
    faces = [(0,1,3),(0,3,2),(4,6,7),(4,7,5),(0,4,5),(0,5,1),(2,3,7),(2,7,6),(0,2,6),(0,6,4),(1,5,7),(1,7,3)]
    return v[np.array(faces)]

def test_write_stl_round_trips(tmp_path):
    tris = cube_tris()
    p = tmp_path / "c.stl"; write_stl(str(p), tris)
    back, n = read_stl(str(p))
    assert n == 12 and np.allclose(back, tris)

def test_write_stl_normals_follow_winding(tmp_path):
    tris = cube_tris()
    p = tmp_path / "c.stl"; write_stl(str(p), tris)
    raw = open(p, "rb").read()[84:]
    normals = np.frombuffer(raw, dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))["n"]
    centroids = tris.mean(axis=1) - 5.0
    assert (np.einsum("ij,ij->i", normals, centroids) > 0).all()

def _shapes_to_step(tmp_path, shapes, name="shapes.step"):
    pytest.importorskip("OCP")
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound
    from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
    builder, comp = BRep_Builder(), TopoDS_Compound()
    builder.MakeCompound(comp)
    for shape in shapes:
        builder.Add(comp, shape)
    w = STEPControl_Writer(); w.Transfer(comp, STEPControl_AsIs)
    path = str(tmp_path / name); w.Write(path)
    return path

def _box_step(tmp_path, boxes):
    pytest.importorskip("OCP")
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.gp import gp_Pnt
    shapes = [BRepPrimAPI_MakeBox(gp_Pnt(x, y, z), dx, dy, dz).Shape() for (x, y, z, dx, dy, dz) in boxes]
    return _shapes_to_step(tmp_path, shapes, name="boxes.step")

def signed_volume_mm3(tris):
    """sum(dot(v0, cross(v1, v2))) / 6 over all triangles. Positive and
    equal to the enclosed volume for a closed, outward-wound mesh."""
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    return float(np.einsum("ij,ij->i", v0, np.cross(v1, v2)).sum() / 6.0)

def test_mesh_step_one_record_per_solid(tmp_path):
    from tools.step_to_mesh import mesh_step
    step = _box_step(tmp_path, [(0, 0, 0, 10, 20, 30), (50, 0, 0, 5, 5, 5)])
    recs = mesh_step(step, str(tmp_path / "out"))
    assert [r["index"] for r in recs] == [0, 1]
    assert np.allclose(recs[0]["bbox_max"], [10, 20, 30]) and np.allclose(recs[0]["bbox_min"], [0, 0, 0])
    assert abs(recs[0]["volume_cm3"] - 6.0) < 1e-6
    assert recs[0]["triangles"] == 12
    tris, _ = read_stl(os.path.join(str(tmp_path / "out"), "solid-0.stl"))
    lo, hi = tris.reshape(-1, 3).min(0), tris.reshape(-1, 3).max(0)
    assert np.allclose(hi - lo, [10, 20, 30])

def test_mesh_step_is_deterministic(tmp_path):
    from tools.step_to_mesh import mesh_step
    step = _box_step(tmp_path, [(0, 0, 0, 10, 10, 10)])
    mesh_step(step, str(tmp_path / "a")); mesh_step(step, str(tmp_path / "b"))
    assert open(tmp_path / "a" / "solid-0.stl", "rb").read() == open(tmp_path / "b" / "solid-0.stl", "rb").read()

def _assert_outward_and_volume_matches(out_dir, recs):
    for r in recs:
        tris, _ = read_stl(os.path.join(out_dir, r["file"]))
        vol = signed_volume_mm3(tris)
        assert vol > 0
        assert abs(vol / 1000.0 - r["volume_cm3"]) / r["volume_cm3"] < 0.02

def test_mesh_step_winding_is_outward(tmp_path):
    pytest.importorskip("OCP")
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from tools.step_to_mesh import mesh_step
    box_step = _box_step(tmp_path, [(0, 0, 0, 10, 20, 30)])
    cyl_step = _shapes_to_step(tmp_path, [BRepPrimAPI_MakeCylinder(5.0, 10.0).Shape()], name="cyl.step")
    for step, out_name in [(box_step, "box_out"), (cyl_step, "cyl_out")]:
        out_dir = str(tmp_path / out_name)
        recs = mesh_step(step, out_dir)
        _assert_outward_and_volume_matches(out_dir, recs)

FLOWER = os.path.join(ROOT, "hardware", "flower-low", "step", "flower-cup-withrim-part.step")

@pytest.mark.skipif(not os.path.exists(FLOWER), reason="hardware not imported")
def test_real_flower_low_has_six_solids(tmp_path):
    pytest.importorskip("OCP")
    from tools.step_to_mesh import mesh_step
    recs = mesh_step(FLOWER, str(tmp_path))
    assert len(recs) == 6
    body = [r for r in recs if r["volume_cm3"] > 5.0]
    assert len(body) == 3   # two cup-body halves + the petal/string solid

@pytest.mark.skipif(not os.path.exists(FLOWER), reason="hardware not imported")
def test_real_flower_low_winding_is_outward(tmp_path):
    pytest.importorskip("OCP")
    from tools.step_to_mesh import mesh_step
    out_dir = str(tmp_path)
    recs = mesh_step(FLOWER, out_dir)
    _assert_outward_and_volume_matches(out_dir, recs)
