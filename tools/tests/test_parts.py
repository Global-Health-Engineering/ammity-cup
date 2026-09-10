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
        "flower-low", "flower-low-section", "flower-low-vs-high", "flower-low-mould",
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
