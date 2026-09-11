import json, os
import numpy as np
import pytest
from tools.parts import SCENES, ROLE_COLORS, UP_TO_Z, Group, mesh_dir
from tools.stl_units import read_stl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_up_to_z_maps_each_axis_to_plus_z():
    axes = {"+x": (1,0,0), "-x": (-1,0,0), "+y": (0,1,0), "-y": (0,-1,0), "+z": (0,0,1), "-z": (0,0,-1)}
    for key, vec in axes.items():
        m = np.array(UP_TO_Z[key])
        assert np.allclose(m @ np.array(vec), [0, 0, 1]), key
        assert np.isclose(np.linalg.det(m), 1.0), key   # a rotation, never a reflection

def test_every_role_has_a_colour():
    for scene in SCENES.values():
        for g in scene.groups:
            roles = set((g.roles or {}).values()) | {g.default_role}
            assert roles <= set(ROLE_COLORS), (scene.name, roles)

def test_every_referenced_step_exists():
    for scene in SCENES.values():
        for g in scene.groups:
            for step in g.steps:
                assert os.path.exists(os.path.join(ROOT, step)), step

def test_expected_scene_names():
    assert set(SCENES) == {
        "flower-sections", "flower-low-vs-high", "flower-low-mould",
        "concept-flower-low", "concept-flower-high", "concept-twister", "concept-umbrella",
        "concept-drawstring", "concept-duckbill", "concept-balloon", "concept-extraction-valve",
        "rig-artificial-vagina"}

needs_meshes = pytest.mark.skipif(
    not os.path.isdir(os.path.join(ROOT, "build", "meshes")), reason="run tools/step_to_mesh.py first")

def _group_points(g, role_filter=None):
    pts = []
    for k, step in enumerate(g.steps):
        d = os.path.join(ROOT, mesh_dir(step))
        for rec in json.load(open(os.path.join(d, "index.json")))["solids"]:
            i = rec["index"]
            if k == 0 and i in g.exclude:
                continue
            role = (g.roles or {}).get(i, g.default_role) if k == 0 else g.default_role
            if role_filter and role != role_filter:
                continue
            pts.append(read_stl(os.path.join(d, rec["file"]))[0].reshape(-1, 3))
    return np.concatenate(pts)

@needs_meshes
@pytest.mark.parametrize("scene", ["concept-flower-low", "concept-flower-high", "concept-twister",
                                   "concept-drawstring", "concept-balloon", "concept-extraction-valve"])
def test_cup_rim_points_up(scene):
    """After orientation the rim (widest cross-section, 41-46 mm) is at the
    top of the body; the stem end is narrower. Compares the radial extent
    of the top and bottom 4 mm of the body-role solids."""
    g = SCENES[scene].groups[0]
    p = _group_points(g, "body") @ np.array(UP_TO_Z[g.up]).T
    cx, cy = (p[:, 0].max() + p[:, 0].min()) / 2, (p[:, 1].max() + p[:, 1].min()) / 2
    r = np.hypot(p[:, 0] - cx, p[:, 1] - cy)
    top, bot = p[:, 2] > p[:, 2].max() - 4, p[:, 2] < p[:, 2].min() + 4
    assert r[top].max() > r[bot].max(), f"{scene}: rim is not up, flip Group.up"

def _area(t):
    return np.linalg.norm(np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]), axis=1) / 2

@needs_meshes
def test_flower_high_splits_into_body_and_mechanism():
    """Flower High's STEP file is one fused solid, so its petals and strings
    are told apart from the cup by geometry (tools.parts.face_roles),
    calibrated on Flower Low's separate solids. Both roles must be present,
    no body face may reach above Flower Low's rim top (+0.2 mm), and the
    mechanism's share of the surface must be close to Flower Low's."""
    from tools.parts import face_roles
    g = SCENES["concept-flower-high"].groups[0]
    split = g.split[0]
    tris = read_stl(os.path.join(ROOT, mesh_dir(g.steps[0]), "solid-0.stl"))[0]
    roles = np.array(face_roles(tris.tolist(), split, ROOT))
    assert set(roles) == {"body", "mechanism"}

    ref_dir = os.path.join(ROOT, mesh_dir(split.reference))
    ref = json.load(open(os.path.join(ref_dir, "index.json")))["solids"]
    rim_top = max(s["bbox_max"][1] for s in ref if s["index"] in split.reference_body)
    assert tris[roles == "body"][:, :, 1].max() <= rim_top + 0.2

    a = _area(tris)
    high_ratio = a[roles == "mechanism"].sum() / a.sum()
    low = {s["index"]: _area(read_stl(os.path.join(ref_dir, s["file"]))[0]).sum() for s in ref}
    low_ratio = sum(v for i, v in low.items() if i not in split.reference_body) / sum(low.values())
    assert abs(high_ratio - low_ratio) <= 0.3 * low_ratio, (high_ratio, low_ratio)

def test_flower_high_is_split_wherever_it_is_shown():
    """Every scene showing Flower High colours its mechanism (no scene
    forces the whole cup to one role any more)."""
    for name in ("flower-sections", "flower-low-vs-high", "concept-flower-high"):
        s = SCENES[name]
        assert s.uniform_role is None, name
        high = [g for g in s.groups if any("flower-high" in p for p in g.steps)]
        assert high and all(g.split for g in high), name

def test_balloon_shows_its_derived_membrane_as_mechanism():
    groups = SCENES["concept-balloon"].groups
    derived = [g for g in groups if g.steps == ("hardware/balloon/step/balloon-top-mould.step",)]
    assert len(derived) == 1
    assert derived[0].derive == "mould-cavity" and derived[0].default_role == "mechanism"
    assert SCENES["concept-balloon"].layout == "flat-lay"

def _box(x0, x1, y0, y1, z0, z1):
    """12 outward triangles of an axis-aligned box."""
    c = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return [(c[a], c[b], c[d]) for a, b, _, d in quads] + [(c[b], c[e], c[d]) for _, b, e, d in quads]

def test_clean_extent_stops_where_thin_slivers_begin():
    """A 5 mm block from y 0 to 10 with a 0.02 mm sheet sticking out of it
    to y 14 (a comb sliver): the clean extent along y is the block."""
    from tools.parts import clean_extent
    tris = _box(0, 5, 0, 10, 0, 5) + _box(2, 2.02, 9, 14, 1, 4)
    axis, lo, hi = clean_extent(tris)
    assert axis == 1
    assert 0 <= lo < 0.5 and 9 - 0.5 < hi < 9, (lo, hi)

def test_drawstring_shows_its_lid_as_mechanism():
    groups = SCENES["concept-drawstring"].groups
    lid = [g for g in groups if g.steps == ("hardware/drawstring/step/drawstring.step",)]
    assert len(lid) == 1 and lid[0].default_role == "mechanism"
    assert SCENES["concept-drawstring"].layout == "flat-lay"
