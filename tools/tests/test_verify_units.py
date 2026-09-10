import struct
import numpy as np
import pytest
from tools.verify_units import check_file, main, MIN_MM, MAX_MM


def write_cube(path, size):
    tri = np.array([[[0, 0, 0], [size, 0, 0], [0, size, 0]],
                    [[0, 0, size], [size, 0, size], [0, size, size]]])
    with open(path, "wb") as f:
        f.write(b"\0" * 80)
        f.write(struct.pack("<I", len(tri)))
        for t in tri:
            f.write(struct.pack("<3f", 0.0, 0.0, 1.0))
            for v in t:
                f.write(struct.pack("<3f", *v))
            f.write(struct.pack("<H", 0))
    return str(path)


def test_metre_scale_file_is_rejected(tmp_path):
    p = write_cube(tmp_path / "bad.stl", 0.077)
    ok, dim, msg = check_file(p)
    assert ok is False
    assert dim == pytest.approx(0.077, abs=1e-6)
    assert "metre" in msg.lower()


def test_millimetre_scale_file_is_accepted(tmp_path):
    p = write_cube(tmp_path / "good.stl", 77.0)
    ok, dim, msg = check_file(p)
    assert ok is True
    assert dim == pytest.approx(77.0, abs=1e-3)


def test_absurdly_large_file_is_rejected(tmp_path):
    p = write_cube(tmp_path / "huge.stl", 5000.0)
    ok, _, msg = check_file(p)
    assert ok is False
    assert str(int(MAX_MM)) in msg


def test_main_returns_zero_when_all_pass(tmp_path):
    a = write_cube(tmp_path / "a.stl", 77.0)
    b = write_cube(tmp_path / "b.stl", 37.3)
    assert main([a, b]) == 0


def test_main_returns_one_when_any_fails(tmp_path):
    good = write_cube(tmp_path / "good.stl", 77.0)
    bad = write_cube(tmp_path / "bad.stl", 0.077)
    assert main([good, bad]) == 1


def test_unreadable_file_fails_without_raising(tmp_path):
    p = tmp_path / "truncated.stl"
    p.write_bytes(b"\0" * 80 + b"\xff\xff\xff\xff" + b"garbage")
    ok, dim, msg = check_file(str(p))
    assert ok is False
    assert "binary STL" in msg


def test_one_bad_file_does_not_abort_the_batch(tmp_path):
    good = write_cube(tmp_path / "good.stl", 77.0)
    bad = tmp_path / "bad.stl"
    bad.write_bytes(b"\0" * 80 + b"\xff\xff\xff\xff" + b"garbage")
    later = write_cube(tmp_path / "later.stl", 37.3)
    assert main([good, str(bad), later]) == 1


def test_no_matching_files_is_a_failure_not_a_silent_pass(tmp_path):
    assert main([str(tmp_path / "nothing-here-*.stl")]) == 1
