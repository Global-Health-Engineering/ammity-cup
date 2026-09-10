import struct
import numpy as np
import pytest
from tools.stl_units import read_stl, bounding_box, max_dimension, rescale_stl


def write_stl(path, triangles):
    """Write a minimal binary STL from an (n,3,3) array."""
    with open(path, "wb") as f:
        f.write(b"\0" * 80)
        f.write(struct.pack("<I", len(triangles)))
        for tri in triangles:
            f.write(struct.pack("<3f", 0.0, 0.0, 1.0))
            for vertex in tri:
                f.write(struct.pack("<3f", *vertex))
            f.write(struct.pack("<H", 0))


@pytest.fixture
def cube_metres(tmp_path):
    """A 0.077 m cube, the defect: correct object, wrong unit."""
    p = tmp_path / "metres.stl"
    tri = np.array([[[0, 0, 0], [0.077, 0, 0], [0, 0.077, 0]],
                    [[0, 0, 0.077], [0.077, 0, 0.077], [0, 0.077, 0.077]]])
    write_stl(p, tri)
    return str(p)


def test_read_stl_returns_triangles_and_count(cube_metres):
    triangles, count = read_stl(cube_metres)
    assert count == 2
    assert triangles.shape == (2, 3, 3)


def test_bounding_box_spans_the_geometry(cube_metres):
    triangles, _ = read_stl(cube_metres)
    lo, hi = bounding_box(triangles)
    assert np.allclose(lo, [0, 0, 0], atol=1e-6)
    assert np.allclose(hi, [0.077, 0.077, 0.077], atol=1e-6)


def test_max_dimension_detects_metre_scale(cube_metres):
    triangles, _ = read_stl(cube_metres)
    assert max_dimension(triangles) == pytest.approx(0.077, abs=1e-6)


def test_rescale_converts_metres_to_millimetres(cube_metres, tmp_path):
    out = str(tmp_path / "mm.stl")
    rescale_stl(cube_metres, out, 1000.0)
    triangles, count = read_stl(out)
    assert count == 2
    assert max_dimension(triangles) == pytest.approx(77.0, abs=1e-3)


def test_rescale_preserves_triangle_count(cube_metres, tmp_path):
    out = str(tmp_path / "mm.stl")
    rescale_stl(cube_metres, out, 1000.0)
    _, before = read_stl(cube_metres)
    _, after = read_stl(out)
    assert before == after
