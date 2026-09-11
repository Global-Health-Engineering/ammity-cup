"""Which solids make up each render, what they are, and how they sit.

Pure Python (no numpy) so Blender's bundled interpreter can import it.
Solid indices refer to build/meshes/<slug>/<stem>/index.json written by
tools/step_to_mesh.py, which preserves the STEP file's own solid order.

A Group is a set of STEP files that share one coordinate frame and can
therefore be shown assembled. Parts from files whose frames differ are
never forced together (that would be a made-up assembly); a scene lays
such groups side by side and its caption says so.
"""
import bisect
import functools
import json
import math
import os
import struct
from dataclasses import dataclass

# Scene-linear Principled BSDF base colours (Standard view transform, so
# displayed sRGB ~ linear^(1/2.2)). Nothing lighter than 0.62, or the part
# loses its silhouette on the site's near-white card (--bg-2 #f6f7f9);
# the same limit 3DPLAM's renders learned. One colour per role in EVERY
# render, so a reader who learns "purple is the closing mechanism" in one
# view carries it to the next.
ROLE_COLORS = {
    "body": (0.42, 0.44, 0.47, 1.0),       # silicone cup body, cool mid grey
    "mechanism": (0.40, 0.09, 0.28, 1.0),  # closing mechanism, GHE magenta (#873671) in linear
    "mould": (0.56, 0.43, 0.16, 1.0),      # printed mould, ochre (3DPLAM's printed-part colour)
    "rig": (0.62, 0.60, 0.57, 1.0),        # test equipment, light warm grey
}

# Rotation matrices (rows) sending the named axis to +Z, det = +1.
UP_TO_Z = {
    "+z": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    "-z": ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
    "+y": ((1, 0, 0), (0, 0, -1), (0, 1, 0)),
    "-y": ((1, 0, 0), (0, 0, 1), (0, -1, 0)),
    "+x": ((0, 0, -1), (0, 1, 0), (1, 0, 0)),
    "-x": ((0, 0, 1), (0, 1, 0), (-1, 0, 0)),
}


def mesh_dir(step):
    """'hardware/<slug>/step/<stem>.step' -> 'build/meshes/<slug>/<stem>'."""
    parts = step.split("/")
    return os.path.join("build", "meshes", parts[1], os.path.splitext(parts[3])[0])


@dataclass(frozen=True)
class FaceSplit:
    """How to split one fused solid into `body` and `mechanism` by geometry.

    Flower High's STEP file is a single fused solid (cup, petal disc,
    petals and strings in one), so solid indices cannot colour it. Flower
    Low's file has the same parts as separate solids in the same frame,
    so it calibrates a geometric rule instead (see face_roles()):

    a face is `mechanism` if its centroid lies above the body's rim top
    (STEP y > rim top + above_mm), or inside the cup wall (radial distance
    from the cup axis < the body's inner wall radius at that height -
    inside_mm). Everything else is `body`.

    The cup axis is the STEP +y axis (the Flower files' `up`), centred on
    the reference body's bounding box in x and z; the rim top and the
    inner wall radius profile are measured from the reference body solids.
    Only the two margins are tuned.
    """
    reference: str            # STEP file whose separate solids calibrate the rule
    reference_body: tuple     # its body-role solid indices
    above_mm: float = 0.2
    inside_mm: float = 0.3


@dataclass(frozen=True)
class Group:
    steps: tuple
    up: str
    default_role: str = "body"
    roles: dict = None
    exclude: tuple = ()
    mirror: tuple = None
    # {solid index: FaceSplit} for fused solids whose roles must be told
    # apart by geometry rather than by solid index (first STEP file only).
    split: dict = None
    # "mould-cavity": the part has no file of its own; steps[0] is its
    # mould, and render_parts derives the part as that mould's cavity.
    derive: str = None


def read_stl_triangles(path):
    """Binary STL -> list of (v0, v1, v2) vertex tuples, in millimetres.
    Pure Python (struct), so Blender's interpreter can use it too."""
    with open(path, "rb") as f:
        f.read(80)
        count = struct.unpack("<I", f.read(4))[0]
        raw = f.read(count * 50)
    return [(r[3:6], r[6:9], r[9:12]) for r in struct.iter_unpack("<12fH", raw)]


PROFILE_STEP_MM = 0.25


@dataclass(frozen=True)
class WallProfile:
    """The reference body's inner wall, as a radius per height (STEP y)."""
    axis_x: float
    axis_z: float
    rim_top: float
    ys: tuple
    radii: tuple

    def inner_radius(self, y):
        """Inner wall radius at height y (linear between samples), or None
        below the lowest sample, where there is no cavity."""
        if y < self.ys[0]:
            return None
        if y >= self.ys[-1]:
            return self.radii[-1]
        k = bisect.bisect_right(self.ys, y) - 1
        t = (y - self.ys[k]) / (self.ys[k + 1] - self.ys[k])
        return self.radii[k] + (self.radii[k + 1] - self.radii[k]) * t

    def radius(self, x, z):
        return math.hypot(x - self.axis_x, z - self.axis_z)


def _segment_min_radius(p, q, ax, az):
    """Smallest distance from the axis (ax, az) to the xz segment p-q."""
    dx, dz = q[0] - p[0], q[1] - p[1]
    n = dx * dx + dz * dz
    t = 0.0 if n == 0 else max(0.0, min(1.0, ((ax - p[0]) * dx + (az - p[1]) * dz) / n))
    return math.hypot(p[0] + dx * t - ax, p[1] + dz * t - az)


@functools.lru_cache(maxsize=None)
def wall_profile(split, root="."):
    """Slice the reference body solids every PROFILE_STEP_MM along y and
    record the smallest radius of each cross-section (the inner wall;
    exact on the tessellated surface, chords included). Each sample is
    then replaced by the minimum of itself and its two neighbours, so a
    step in the wall (a groove, the stem shoulder) never makes the linear
    interpolation between samples run past the real wall."""
    d = os.path.join(root, mesh_dir(split.reference))
    with open(os.path.join(d, "index.json")) as f:
        solids = [s for s in json.load(f)["solids"] if s["index"] in split.reference_body]
    lo = [min(s["bbox_min"][i] for s in solids) for i in range(3)]
    hi = [max(s["bbox_max"][i] for s in solids) for i in range(3)]
    ax, az, rim_top = (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2, hi[1]
    step = PROFILE_STEP_MM
    y0 = math.floor(lo[1] / step) * step
    n = int(math.floor((rim_top - y0) / step)) + 1
    prof = [math.inf] * n
    for s in solids:
        for tri in read_stl_triangles(os.path.join(d, s["file"])):
            a, b, c = sorted(tri, key=lambda v: v[1])
            if c[1] == a[1]:
                continue
            k0 = max(0, math.ceil((a[1] - y0) / step))
            k1 = min(n - 1, math.floor((c[1] - y0) / step))
            for k in range(k0, k1 + 1):
                y = y0 + k * step
                t = (y - a[1]) / (c[1] - a[1])
                p = (a[0] + (c[0] - a[0]) * t, a[2] + (c[2] - a[2]) * t)
                u, v = (a, b) if y <= b[1] else (b, c)
                if v[1] == u[1]:
                    q = (u[0], u[2])
                else:
                    t = (y - u[1]) / (v[1] - u[1])
                    q = (u[0] + (v[0] - u[0]) * t, u[2] + (v[2] - u[2]) * t)
                r = _segment_min_radius(p, q, ax, az)
                if r < prof[k]:
                    prof[k] = r
    keep = [k for k in range(n) if prof[k] < math.inf]
    ys = tuple(y0 + k * step for k in keep)
    vals = [prof[k] for k in keep]
    radii = tuple(min(vals[max(0, i - 1):i + 2]) for i in range(len(vals)))
    return WallProfile(ax, az, rim_top, ys, radii)


def face_roles(triangles, split, root="."):
    """'body' or 'mechanism' for each triangle (three xyz vertices, mm, in
    the STEP frame), by FaceSplit's rule, calibrated on its reference."""
    p = wall_profile(split, root)
    top = p.rim_top + split.above_mm
    roles = []
    for a, b, c in triangles:
        cx, cy, cz = ((a[i] + b[i] + c[i]) / 3 for i in range(3))
        if cy > top:
            roles.append("mechanism")
            continue
        r_in = p.inner_radius(cy)
        inside = r_in is not None and p.radius(cx, cz) < r_in - split.inside_mm
        roles.append("mechanism" if inside else "body")
    return roles


SLICE_STEP_MM = 0.25
# Slice planes sit this far off the step grid so they never pass exactly
# through a vertex (a CAD mesh has many vertices on round coordinates),
# where a cross-section chain would break.
SLICE_OFFSET_MM = 0.0137
# A cross-section loop whose mean width (2 x area / perimeter) is below
# this is a sliver sheet, not part of the moulded part. The
# balloon cavity's comb slivers measure 0.00-0.03 mm; its real loops,
# neck and vent stubs included, are 1.3 mm and more.
THIN_MM = 0.15


def _cross_section(tris, axis, level):
    """Loops of the section of `tris` by the plane axis = level, as a list
    of (area, perimeter, closed). Segment ends are keyed by the mesh edge
    they lie on, so chaining never depends on float rounding."""
    u, v = [i for i in range(3) if i != axis]
    ends = {}
    segs = []
    for tri in tris:
        keys = []
        for i, j in ((0, 1), (1, 2), (2, 0)):
            a, b = tri[i], tri[j]
            if (a[axis] < level) != (b[axis] < level):
                a, b = sorted((tuple(a), tuple(b)))
                s = (level - a[axis]) / (b[axis] - a[axis])
                key = (a, b)
                ends[key] = (a[u] + (b[u] - a[u]) * s, a[v] + (b[v] - a[v]) * s)
                keys.append(key)
        if len(keys) == 2:
            segs.append(keys)
    by_end = {}
    for n, (p, q) in enumerate(segs):
        by_end.setdefault(p, []).append(n)
        by_end.setdefault(q, []).append(n)
    used = [False] * len(segs)
    loops = []
    for n in range(len(segs)):
        if used[n]:
            continue
        used[n] = True
        start, cur = segs[n]
        pts = [ends[start], ends[cur]]
        while cur != start:
            nxt = [m for m in by_end[cur] if not used[m]]
            if not nxt:
                break
            used[nxt[0]] = True
            p, q = segs[nxt[0]]
            cur = q if p == cur else p
            pts.append(ends[cur])
        area = abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:]))) / 2
        perim = sum(math.hypot(x1 - x0, y1 - y0) for (x0, y0), (x1, y1) in zip(pts, pts[1:]))
        loops.append((area, perim, cur == start))
    return loops


def clean_extent(triangles, step=SLICE_STEP_MM, thin_mm=THIN_MM):
    """Where along its longest axis a mesh is free of sliver sheets.

    Slices the mesh every `step` mm along the axis of its largest
    bounding-box extent. A slice is clean when every loop of its section
    closes and none is thinner than `thin_mm` (area/perimeter). Returns
    (axis, lo, hi): the first and last slice of the clean run that holds
    the largest section, so cutting there keeps the body and drops every
    sliver that starts past it."""
    lo_b = [min(t[k][i] for t in triangles for k in range(3)) for i in range(3)]
    hi_b = [max(t[k][i] for t in triangles for k in range(3)) for i in range(3)]
    axis = max(range(3), key=lambda i: hi_b[i] - lo_b[i])
    l0 = lo_b[axis] + SLICE_OFFSET_MM
    n = int((hi_b[axis] - l0) / step) + 1
    buckets = [[] for _ in range(n)]
    for tri in triangles:
        a = [p[axis] for p in tri]
        for k in range(max(0, math.ceil((min(a) - l0) / step)),
                       min(n - 1, math.floor((max(a) - l0) / step)) + 1):
            buckets[k].append(tri)
    clean, area = [], []
    for k in range(n):
        loops = _cross_section(buckets[k], axis, l0 + k * step)
        clean.append(bool(loops) and all(c and p > 0 and a / p >= thin_mm / 2 for a, p, c in loops))
        area.append(sum(a for a, _, _ in loops))
    k = max(range(n), key=lambda i: area[i] if clean[i] else -1)
    if not clean[k]:
        raise ValueError("no clean cross-section found")
    k0 = k1 = k
    while k0 > 0 and clean[k0 - 1]:
        k0 -= 1
    while k1 < n - 1 and clean[k1 + 1]:
        k1 += 1
    return axis, l0 + k0 * step, l0 + k1 * step


def mechanism_region(split, root, far_r, top_y):
    """The same rule as a solid of revolution about the cup axis: its
    (radius, y) outline in mm, from the axis at the lowest wall sample,
    along the inner wall radius minus inside_mm up to the rim top plus
    above_mm, then out to `far_r` and up to `top_y`. A face lies in this
    region exactly when face_roles() calls it `mechanism`, so render_parts
    can split a fused solid with two booleans (and so with clean, closed
    pieces and crisp borders) instead of face by face."""
    p = wall_profile(split, root)
    lim = p.rim_top + split.above_mm

    def r_at(r_in):
        return max(r_in - split.inside_mm, 0.01)

    pts = [(0.0, p.ys[0])]
    pts += [(r_at(r), y) for y, r in zip(p.ys, p.radii) if y <= lim]
    pts += [(r_at(p.inner_radius(lim)), lim), (far_r, lim), (far_r, top_y), (0.0, top_y)]
    return pts, (p.axis_x, p.axis_z)


@dataclass(frozen=True)
class Scene:
    name: str
    groups: tuple
    layout: str
    caption: str
    # 800, not 1000: Task 8's first render pass put renders+models at 25.2
    # MB against a 20 MB budget; dropping every scene that relies on this
    # default (the 8 concept-* scenes and rig-artificial-vagina) to 800px
    # is the controller-authorized first lever (see Task 8 brief). The
    # three Device scenes (flower-sections, flower-low-vs-high,
    # flower-low-mould) set resolution=2000 explicitly below.
    resolution: int = 800
    uniform_role: str = None
    # Fix round 2: an optional camera-direction override, (x, y, z) in the
    # world frame *after* each group's own orientation (see UP_TO_Z), the
    # same frame `view` variables inside render_parts.build() already use.
    # None (every scene but concept-drawstring) keeps today's per-layout
    # default (ISO, or the flatter flat-lay/section angles); render_parts
    # substitutes Vector(view) instead when it is set.
    view: tuple = None


def _hw(slug, stem):
    return f"hardware/{slug}/step/{stem}.step"


FLOWER_LOW = Group(
    steps=(_hw("flower-low", "flower-cup-withrim-part"),),
    up="+y",
    roles={0: "body", 1: "body", 2: "body", 3: "body", 4: "mechanism", 5: "mechanism"},
)
# Flower Low's solids 0-3 are the cup (body halves and the two small
# pieces at the stem end); 4 and 5 are the petal disc and the
# petals-with-strings. Margins: see FaceSplit and task-18's report.
FLOWER_SPLIT = FaceSplit(reference=_hw("flower-low", "flower-cup-withrim-part"),
                         reference_body=(0, 1, 2, 3))
FLOWER_HIGH = Group(steps=(_hw("flower-high", "flower-cup-withrim-higher"),), up="+y",
                    split={0: FLOWER_SPLIT})
FLOWER_LOW_MOULD = Group(
    steps=(_hw("flower-low", "flower-cup-withrim-mould"),), up="+z", default_role="mould")

CONCEPT_GROUPS = {
    "flower-low": (FLOWER_LOW,),
    "flower-high": (FLOWER_HIGH,),
    "twister": (
        Group(steps=(_hw("twister", "twister-cup-top"), _hw("twister", "twister-cup-bottom-withdent")),
              up="+y", default_role="body"),
        Group(steps=(_hw("twister", "twister-skin"),), up="+z", default_role="mechanism"),
    ),
    "umbrella": (
        Group(steps=(_hw("umbrella", "menstrual-cup-medium-without-umbrella"),), up="+y",
              mirror=("z", 0.0)),
        Group(steps=(_hw("umbrella", "umbrella-top-open-full"),), up="+z", default_role="mechanism"),
        Group(steps=(_hw("umbrella", "umbrella-contain-silicone"),), up="+z", default_role="mechanism"),
    ),
    "drawstring": (
        Group(steps=(_hw("drawstring", "menstrual-cup-medium-drawstring"),), up="+y",
              roles={0: "body", 1: "mechanism", 2: "mechanism", 3: "mechanism",
                     4: "mechanism", 5: "mechanism", 6: "mechanism"}),
        # The lid, modelled flat (124.6 x 66.3 x 7.6 mm): a 1.3 mm plate
        # whose large flat face is its STEP z = 0 face, so +z puts that
        # face down (a small tab at one end reaches 2.3 mm below it, the
        # only part lower than the plate).
        Group(steps=(_hw("drawstring", "drawstring"),), up="+z", default_role="mechanism"),
    ),
    "duckbill": (
        Group(steps=(_hw("duckbill", "duckbill-half-withrim"),), up="+y", exclude=(1,),
              mirror=("z", 0.0)),
    ),
    "balloon": (
        Group(steps=(_hw("balloon", "menstrual-cup-medium-without-balloon"),
                     _hw("balloon", "balloon-pipe")), up="+y"),
        # The balloon itself has no part file, only its mould: derived as
        # the mould's cavity (render_parts.derive_mould_cavity). Its bulb
        # is flat in the mould's xy plane, so +z lays it flat.
        Group(steps=(_hw("balloon", "balloon-top-mould"),), up="+z", default_role="mechanism",
              derive="mould-cavity"),
    ),
    "extraction-valve": (
        Group(steps=(_hw("extraction-valve", "menstrual-cup-valve"),), up="+y"),
        Group(steps=(_hw("extraction-valve", "cup-valve-button"),), up="+z", default_role="mechanism"),
    ),
}

CONCEPT_CAPTIONS = {
    "flower-low": "Flower Low: five petals at the opening, each joined by a silicone string to the "
                  "pull mechanism in the stem; the strings are shown straight, as cast.",
    "flower-high": "Flower High: the same mechanism with the petal bases nearer the rim.",
    "twister": "Twister: top and bottom sections; the thin membrane skin that joins them is shown beside them.",
    "umbrella": "Umbrella: cup body, the umbrella insert, and its silicone housing, shown side by side.",
    "drawstring": "Drawstring: cup body, and the lid that closes it (purple), shown flat as moulded; "
                  "in the cup the lid is folded against the inner wall.",
    "duckbill": "Duckbill: moulded as two halves and joined; shown as the mirrored pair.",
    "balloon": "Balloon: cup body and bulb pipe; the balloon (purple) is shown as the cavity of its "
               "mould, with the vent and core-pin channels trimmed, since no part file for it exists.",
    "extraction-valve": "Extraction valve: cup body and valve button, shown side by side. Untested concept.",
}

# Fix round 2: fix round 1's layout="section" for concept-drawstring cut
# through solid 0 (body) and left a sharp-edged near-black patch (likely
# inside-out faces from cut_half's boolean on that solid's geometry), and
# still didn't make the mechanism legible (the six small mechanism solids
# sit behind two much larger body-coloured guide tabs that are part of
# solid 0, not a separate mechanism index). Reverted to layout="assembled"
# (no boolean) and instead looks down into the open rim, where the
# mechanism tabs sit, via the `view` override below.
#
# (0.0, 0.45, 1.5), not the brief's example (0.3, -0.5, 1.4): every
# mechanism solid's bounding box sits on the +Y side of the body (in the
# render frame, after orient()), so a -Y camera (the example, and every
# other layout's default) looks at the wall *without* any mechanism on
# it. Measured (alpha-masked, opaque pixels only) while tuning:
#   (0.1, -1.0, 0.5)  0.072%   (0.1, -1.0, 1.2)  0.084%
#   (0.6, -0.8, 1.0)  0.092%   (0.0,  0.0,  1.0)  0.065%
#   (0.0,  0.3, 1.6)  0.112%   (0.0,  0.45, 1.5)  0.137%  <- chosen
# Every view with a *larger* +Y component (tried up to (0.1, 1.0, 1.2),
# 1.58%) exposes far more mechanism but also a sharp-edged purple/grey
# speckle on the outer wall that grows with the +Y component and persists
# across very different elevations, a stable, parallax-consistent
# artifact (almost certainly near-coincident body/mechanism surfaces in
# the source CAD, not camera-angle noise), not something `view` tuning
# can dodge past this point. 0.137% is the most purple obtained with no
# such artifact visible (checked at 2x-4x crops, not just the full frame).
CONCEPT_VIEWS = {"drawstring": (0.0, 0.45, 1.5)}

SCENES = {}
for slug, groups in CONCEPT_GROUPS.items():
    SCENES[f"concept-{slug}"] = Scene(
        name=f"concept-{slug}", groups=groups,
        layout="assembled" if len(groups) == 1 else "flat-lay",
        caption=CONCEPT_CAPTIONS[slug],
        view=CONCEPT_VIEWS.get(slug))

SCENES.update({
    # Section layout cuts each group through its own axis; the two cups
    # come from different STEP files, so they stand side by side.
    "flower-sections": Scene("flower-sections", (FLOWER_LOW, FLOWER_HIGH), "section",
                             "Cut through Flower Low (left) and Flower High (right): the cup "
                             "wall, and the petals seated inside the rim.",
                             resolution=2000),
    "flower-low-vs-high": Scene("flower-low-vs-high", (FLOWER_LOW, FLOWER_HIGH), "flat-lay",
                                "Flower Low (left, flown) and Flower High (right).", resolution=2000),
    "flower-low-mould": Scene("flower-low-mould", (FLOWER_LOW_MOULD, FLOWER_LOW), "exploded",
                              "The printed mould for Flower Low, opened at its parting plane, with the cast cup.",
                              resolution=2000),
    "rig-artificial-vagina": Scene(
        "rig-artificial-vagina",
        (Group(steps=(_hw("artificial-vagina", "parabolicflight-vagina"),), up="+z", default_role="rig"),),
        "assembled", "The artificial vagina test model, cast in silicone from a printed mould."),
})
