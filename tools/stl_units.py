"""Binary STL geometry primitives.

STL carries no unit metadata, so every slicer assumes millimetres. These
helpers let CI prove the shipped mould pieces really are in millimetres.
"""
import struct
import numpy as np

HEADER_BYTES = 80
TRIANGLE_BYTES = 50


def read_stl(path):
    """Read a binary STL. Returns (triangles (n,3,3) float64, count)."""
    with open(path, "rb") as f:
        f.read(HEADER_BYTES)
        count = struct.unpack("<I", f.read(4))[0]
        raw = f.read(count * TRIANGLE_BYTES)
    if len(raw) < count * TRIANGLE_BYTES:
        raise ValueError(f"{path}: truncated, expected {count} triangles")
    data = np.frombuffer(raw, dtype=np.uint8).reshape(count, TRIANGLE_BYTES)
    floats = data[:, :48].copy().view(np.float32).reshape(count, 12)
    return floats[:, 3:12].reshape(count, 3, 3).astype(np.float64), count


def bounding_box(triangles):
    """Return (lo, hi) corner arrays of shape (3,)."""
    points = triangles.reshape(-1, 3)
    return points.min(axis=0), points.max(axis=0)


def max_dimension(triangles):
    """Largest edge of the axis-aligned bounding box."""
    lo, hi = bounding_box(triangles)
    return float((hi - lo).max())


def rescale_stl(src, dst, factor):
    """Copy src to dst with every vertex scaled by factor.

    Normals are deliberately left untouched: they are unit direction
    vectors, so under a uniform positive scale they are already correct.
    Scaling them would produce length-`factor` "unit" normals that some
    consumers reject.
    """
    with open(src, "rb") as f:
        header = f.read(HEADER_BYTES)
        count = struct.unpack("<I", f.read(4))[0]
        raw = bytearray(f.read(count * TRIANGLE_BYTES))
    for i in range(count):
        off = i * TRIANGLE_BYTES
        vals = list(struct.unpack("<12f", raw[off:off + 48]))
        scaled = vals[:3] + [v * factor for v in vals[3:12]]
        raw[off:off + 48] = struct.pack("<12f", *scaled)
    with open(dst, "wb") as f:
        f.write(header)
        f.write(struct.pack("<I", count))
        f.write(bytes(raw))
