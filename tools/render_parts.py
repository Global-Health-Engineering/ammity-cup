"""Headless Blender renders of the SpaceCup variants, plus web models.

Run (meshes first, see tools/step_to_mesh.py):
    .venv/bin/python tools/step_to_mesh.py
    blender --background --python tools/render_parts.py            # all scenes
    blender --background --python tools/render_parts.py -- flower-low   # one scene

Scenes, part roles, orientation and mirroring are declared in
tools/parts.py; this file only turns them into pictures. Every scene is
rendered to site/public/renders/<name>.png and exported, from the same
Blender scene, to site/public/models/<name>.glb for the site's
click-to-open 3D viewer, so a part has the same colour and shape in both.

Meshes are millimetres. Blender's STL importer treats the numbers as
metres, so every import is scaled by 0.001 and the scale applied at once;
after that every coordinate here is genuine metres (mm / 1000).

Camera framing, the section plane and the exploded offsets are computed
from the imported geometry's bounding boxes, never hardcoded, so the
script keeps working if the CAD is revised.

Requires Blender 5.2 LTS (bpy.ops.wm.stl_import; shade_auto_smooth).
The helpers from reset() to export_glb() are carried over unchanged from
3DPLAM's tools/render_parts.py, where their comments explain the choices
(Standard view transform, Cycles on Metal, FOV-derived camera distance,
the shadow catcher, planar-then-collapse decimation).
"""
import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.parts import ROLE_COLORS, SCENES, UP_TO_Z, mesh_dir  # noqa: E402

OUT = os.path.join(ROOT, "site", "public", "renders")
MODELS_OUT = os.path.join(ROOT, "site", "public", "models")
RES = 2000
MM = 0.001
SAMPLES = 256
ISO = Vector((1.0, -1.0, 0.8))


def mm(x):
    """Convert a literal millimetre value (for things this script adds,
    like the membrane or a crop radius) into scene units."""
    return x * MM


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = True
    scene.render.film_transparent = True
    scene.render.resolution_x = RES
    scene.render.resolution_y = RES
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    # Blender 5.2 defaults to the AgX view transform, which rolls off
    # highlights and desaturates strongly, it turned the intended muted
    # teal/ochre/terracotta of the membrane-clamp figure into washed-out
    # pastels, and likely made the original near-white plastic look even
    # paler than its base colour alone would. Standard renders the
    # material's base colour with predictable, non-filmic contrast, which
    # these technical/diagrammatic renders want more than photographic
    # highlight rolloff.
    scene.view_settings.view_transform = "Standard"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        scene.cycles.device = "GPU"
        print(f"  cycles device: GPU ({[d.name for d in prefs.devices if d.use]})")
    except Exception as exc:
        scene.cycles.device = "CPU"
        print(f"  cycles device: CPU (GPU setup failed: {exc})")
    return scene


def matte_material(name, color, roughness=0.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def set_material(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


KEY_ENERGY = 30
KEY_DIST = 3.2  # metres, matches the "key" entry below


def lighting(center, fill_dir=None, fill_radius=None, fill_strength=3.0):
    """Three-point studio lighting aimed at `center` (a Vector), plus a
    soft white world for ambient fill. film_transparent hides the world
    from camera rays but it still contributes bounce light.

    A boolean cut leaves a flat face oriented straight at the camera; the
    generic three-point rig above (all placed metres away, effectively
    directional) barely grazes it, so a cut render reads as a dark band.
    Pass `fill_dir`/`fill_radius` (the camera's direction and the
    scene's own geometric radius) to add a light from near the viewer's
    position, close enough to actually illuminate that face.

    Its energy is *not* copied from the key light: at a much shorter
    distance, the same wattage massively overexposes the shot (this
    happened on the first attempt, irradiance falls off with the square
    of distance, so reusing a far light's power up close floods it).
    Instead it is derived from the key light's own irradiance at its
    distance, scaled to the new distance, times `fill_strength`.

    The world's ambient strength and the fill/rim energies are kept low
    relative to the key (roughly 4:1 key-to-fill) so that form is carried
    by shading gradients rather than washed flat, with the original
    near-white plastic and a strong flat ambient, mid-tones and shadow
    fell in too narrow a range to read as depth."""
    world = bpy.data.worlds.new("studio")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.05
    bpy.context.scene.world = world

    target = bpy.data.objects.new("light-target", None)
    target.location = center
    bpy.context.collection.objects.link(target)

    lights = [
        ("key", Vector((0.6, -0.8, 0.9)), KEY_DIST, KEY_ENERGY, 0.6),
        ("fill", Vector((-0.8, -0.4, 0.4)), 3.6, 8, 0.9),
        ("rim", Vector((0.0, 0.9, 0.6)), 3.4, 10, 0.7),
    ]
    if fill_dir is not None:
        dist = max(fill_radius * 2.5, 0.05)
        energy = KEY_ENERGY * (dist / KEY_DIST) ** 2 * fill_strength
        size = fill_radius * 0.6
        lights.append(("cut-fill", fill_dir, dist, energy, size))
        print(f"  cut-fill light: dist={dist:.4f} energy={energy:.3f} size={size:.4f}")

    for name, direction, dist, energy, size in lights:
        light = bpy.data.lights.new(name, type="AREA")
        light.energy = energy
        light.size = max(size, 0.01)
        obj = bpy.data.objects.new(name, light)
        obj.location = center + direction.normalized() * dist
        bpy.context.collection.objects.link(obj)
        track = obj.constraints.new("TRACK_TO")
        track.track_axis = "TRACK_NEGATIVE_Z"
        track.up_axis = "UP_Y"
        track.target = target


def import_and_prepare(path):
    """Import an STL, fix its units, shade it, return the bare object
    (no material, callers assign one so multi-body scenes can colour
    parts differently)."""
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=os.path.abspath(path))
    obj = (set(bpy.data.objects) - before).pop()
    obj.scale = (MM, MM, MM)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_auto_smooth(angle=math.radians(30))
    return obj


def world_bbox(obj):
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    xs = [c.x for c in corners]
    ys = [c.y for c in corners]
    zs = [c.z for c in corners]
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))


def combined_bbox(objs):
    mins, maxs = zip(*(world_bbox(o) for o in objs))
    lo = Vector((min(v.x for v in mins), min(v.y for v in mins), min(v.z for v in mins)))
    hi = Vector((max(v.x for v in maxs), max(v.y for v in maxs), max(v.z for v in maxs)))
    return lo, hi


def bbox_center(lo, hi):
    return (lo + hi) / 2


def bbox_radius(lo, hi):
    """Half the bounding box's diagonal: a true bounding-sphere radius.
    Unlike `max(dimensions)`, a sphere of this radius is guaranteed to
    contain the whole box from *any* viewing direction, which matters for
    the 3/4 and tilted views used throughout this script."""
    return (hi - lo).length / 2


def cut_half(obj, center, axis=1, keep_positive=True):
    """Boolean-difference away the half of `obj` on the removed side of
    `center[axis]` along `axis` (0=X, 1=Y, 2=Z), leaving the other half
    with a flat cross-section at that plane."""
    size = max(obj.dimensions) * 6 + mm(5)
    bpy.ops.mesh.primitive_cube_add(size=size)
    cutter = bpy.context.active_object
    cutter.location = Vector(center)
    offset = size / 2
    cutter.location[axis] += -offset if keep_positive else offset
    mod = obj.modifiers.new("section", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cutter
    mod.solver = "EXACT"
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="section")
    bpy.data.objects.remove(cutter, do_unlink=True)


SENSOR_WIDTH = 36.0  # mm, Blender's default camera sensor width


def frame_camera(center, radius, direction, lens=85, margin=1.15):
    """Place a tracked camera looking at `center` from `direction` (need
    not be normalized), at the closest distance that keeps a sphere of
    `radius` entirely inside the lens's field of view, computed from the
    lens's actual angle, not a guessed multiplier, so nothing at the
    frame edges gets clipped. TRACK_TO keeps `center` exactly in the
    middle of the frame regardless of `direction`, so a tilted or 3/4
    `direction` never throws the composition off-centre, only `radius`
    and `margin` control how much is visible. Returns the camera
    distance, for callers that want to place a light relative to it."""
    half_fov = math.atan((SENSOR_WIDTH / 2) / lens)
    dist = (radius * margin) / math.sin(half_fov)
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = lens
    cam_data.sensor_width = SENSOR_WIDTH
    # Blender's default near-clip (0.1 m) silently clips the entire
    # subject out of a tight close-up: the membrane-clamp crop sits the
    # camera ~70 mm from its focus, inside that default, which produced a
    # fully transparent render with no error. 1 mm is safe at every scale
    # this script uses.
    cam_data.clip_start = mm(1)
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = Vector(center) + direction.normalized() * dist
    track = cam.constraints.new("TRACK_TO")
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    empty = bpy.data.objects.new("cam-target", None)
    empty.location = center
    bpy.context.collection.objects.link(empty)
    track.target = empty
    bpy.context.scene.camera = cam
    return dist


def add_shadow_catcher(lo, hi, margin_factor=8.0):
    """A large plane at the lowest point of the scene (`lo.z`), marked as
    a Cycles shadow catcher so it renders *only* the soft contact shadow
    the geometry casts on it; the plane itself stays invisible. Combined
    with `film_transparent`, the shadowed pixels get partial alpha rather
    than none, so the shadow survives into the PNG and composites onto
    whatever background the page puts under it. Without this, a
    transparent-background render leaves objects looking like they float
    with no grounding."""
    cx, cy = (lo.x + hi.x) / 2, (lo.y + hi.y) / 2
    size = max(hi.x - lo.x, hi.y - lo.y) * margin_factor
    bpy.ops.mesh.primitive_plane_add(size=size, location=(cx, cy, lo.z))
    plane = bpy.context.active_object
    plane.name = "shadow-catcher"
    set_material(plane, matte_material("shadow-catcher-mat", (1, 1, 1, 1), roughness=0.9))
    plane.is_shadow_catcher = True
    return plane


def render(scene, name):
    os.makedirs(OUT, exist_ok=True)
    scene.render.filepath = os.path.join(OUT, f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"  rendered {name}.png")


def tri_count(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def decimate_for_web(obj, max_tris):
    """Reduce `obj` to roughly `max_tris` triangles for browser delivery.

    Two passes, cheapest first. Planar dissolve merges faces that are
    coplanar within a small angle, on meshes tessellated out of CAD it
    removes a large share of the triangles while changing the silhouette
    by nothing at all, because the removed edges were interior to flat
    regions. Only if that alone misses the budget does collapse
    decimation run, which does move vertices and so is kept as the
    fallback rather than the first move.

    Call this AFTER rendering: the render must use the full-resolution
    mesh, and both modifiers are applied destructively.
    """
    before = tri_count(obj)
    if before <= max_tris:
        print(f"    {obj.name}: {before:,} tris, under budget, untouched")
        return

    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new("planar", "DECIMATE")
    mod.decimate_type = "DISSOLVE"
    mod.angle_limit = math.radians(3.0)
    bpy.ops.object.modifier_apply(modifier="planar")
    after_planar = tri_count(obj)

    if after_planar > max_tris:
        mod = obj.modifiers.new("collapse", "DECIMATE")
        mod.decimate_type = "COLLAPSE"
        mod.ratio = max_tris / after_planar
        bpy.ops.object.modifier_apply(modifier="collapse")
    after = tri_count(obj)
    print(f"    {obj.name}: {before:,} -> {after_planar:,} (planar) -> "
          f"{after:,} tris (budget {max_tris:,})")


def export_glb(name, objs, max_tris=60000):
    """Write `objs` to site/public/models/<name>.glb.

    Only the named objects are exported (no camera, no lights, no shadow
    catcher) because the viewer supplies its own. Materials come along,
    which is what keeps the 3D colours identical to the render's without
    a second palette defined in JavaScript.
    """
    os.makedirs(MODELS_OUT, exist_ok=True)
    for obj in objs:
        decimate_for_web(obj, max_tris)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]

    path = os.path.join(MODELS_OUT, f"{name}.glb")
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        # glTF is Y-up; Blender is Z-up. Without this the model arrives in
        # three.js lying on its side.
        export_yup=True,
    )
    print(f"  exported {name}.glb ({os.path.getsize(path) / 1e6:.2f} MB)")


_ROLE_MATERIALS = {}


def role_material(role):
    """One shared material per role, so every part of that role in every
    scene is the identical colour (see ROLE_COLORS in tools/parts.py)."""
    mat = _ROLE_MATERIALS.get(role)
    stale = mat is None
    if not stale:
        try:
            stale = mat.name not in bpy.data.materials
        except ReferenceError:
            # reset() (called once per scene, from build()) does
            # read_factory_settings(use_empty=True), which frees every
            # material in bpy.data; the cached Python reference to last
            # scene's material then raises on any attribute access
            # instead of behaving like a plain missing key, which crashed
            # a multi-scene run (e.g. `-- concept-twister concept-umbrella`)
            # partway through the second scene. Bug fix, not a tuning
            # change: this function is unchanged from the brief otherwise.
            stale = True
    if stale:
        _ROLE_MATERIALS[role] = matte_material(f"silicone-{role}", ROLE_COLORS[role])
    return _ROLE_MATERIALS[role]


def transform_mesh(objs, matrix):
    """Apply `matrix` to the mesh data itself (not the object transform),
    so bounding boxes, booleans and the glTF export all see the result."""
    for obj in objs:
        obj.data.transform(matrix)
        obj.data.update()
    bpy.context.view_layer.update()


def mirror_copy(obj, axis, at_mm):
    """A mirrored duplicate of `obj` across the plane `axis` = at_mm.

    Several cups are modelled as one half (the mould is split on the
    symmetry plane); the other half is this reflection. A reflection turns
    every triangle inside out, so the face winding is reversed afterwards,
    or Cycles shades the copy as if lit from inside."""
    dup = obj.copy()
    dup.data = obj.data.copy()
    bpy.context.collection.objects.link(dup)
    i = "xyz".index(axis)
    m = Matrix.Identity(4)
    m[i][i] = -1.0
    m[i][3] = 2.0 * mm(at_mm)
    dup.data.transform(m)
    bm = bmesh.new()
    bm.from_mesh(dup.data)
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
    bm.to_mesh(dup.data)
    bm.free()
    dup.data.update()
    return dup


def load_group(group, uniform_role=None):
    """Import every solid of a tools.parts.Group, coloured by role, in the
    STEP files' own coordinate frame (metres)."""
    objs = []
    for k, step in enumerate(group.steps):
        d = os.path.join(ROOT, mesh_dir(step))
        index_path = os.path.join(d, "index.json")
        if not os.path.exists(index_path):
            raise SystemExit(f"{index_path} missing: run tools/step_to_mesh.py first")
        with open(index_path) as f:
            solids = json.load(f)["solids"]
        for rec in solids:
            i = rec["index"]
            if k == 0 and i in group.exclude:
                continue
            role = (group.roles or {}).get(i, group.default_role) if k == 0 else group.default_role
            role = uniform_role or role
            obj = import_and_prepare(os.path.join(d, rec["file"]))
            obj.name = f"{os.path.basename(d)}-{i}"
            obj["role"] = role
            set_material(obj, role_material(role))
            objs.append(obj)
    if group.mirror:
        axis, at = group.mirror
        objs += [mirror_copy(o, axis, at) for o in list(objs)]
    return objs


def orient(objs, up):
    transform_mesh(objs, Matrix(UP_TO_Z[up]).to_4x4())


def place(objs, x_start):
    """Move a group so its bounding box starts at x = x_start, is centred
    on y = 0 and sits on z = 0. Returns the group's width."""
    lo, hi = combined_bbox(objs)
    shift = Vector((x_start - lo.x, -(lo.y + hi.y) / 2, -lo.z))
    transform_mesh(objs, Matrix.Translation(shift))
    return hi.x - lo.x


FLAT_LAY_GAP_MM = 12

# Fix round 1: lighting()'s fill_strength default (3.0) was written for a
# tight crop right on the cut interface (3DPLAM's membrane-clamp shot,
# where the cut face fills most of the frame and the light barely spills
# past it). Section here frames the *whole* cup, so that same strength
# also floods the already-lit outer wall and the mechanism, not just the
# cut face it was meant for: measured 3.2-3.3x brighter (linear) on body
# and 4.3-4.6x on mechanism than the same roles in flower-low.png, which
# breaks the one-colour-per-role rule. 0.12 was chosen by sampling
# alpha-masked body/mechanism patch means against flower-low.png and
# lowering until every channel landed within 15% (see task-8-report.md
# for the numbers), while the cut face itself (checked visually) still
# reads as a lit surface rather than a black band.
CUT_FILL_STRENGTH = 0.12


def build_exploded(mould, cup):
    """The mould opened at its parting plane, the cast cup beside it.

    Mould and cup share the STEP frame; the cup's two body halves meet at
    the mould's parting plane, so the cup's bbox centre height IS that
    plane. Each mould piece moves away from it in proportion to its own
    distance from it, so outer shells travel further than the cores
    and nothing ends up interpenetrating. EXPLODE is empirical, tuned for
    legibility, not to scale (as 3DPLAM's exploded gaps were)."""
    EXPLODE = 2.2
    lo, hi = combined_bbox(cup)
    parting_z = (lo.z + hi.z) / 2
    for obj in mould:
        olo, ohi = world_bbox(obj)
        obj.location.z += ((olo.z + ohi.z) / 2 - parting_z) * EXPLODE
    bpy.context.view_layer.update()
    mlo, mhi = combined_bbox(mould)
    for obj in cup:
        obj.location.x += (mhi.x - lo.x) + mm(15)
    bpy.context.view_layer.update()
    return mould + cup


def build(scene_def):
    scene = reset()
    scene.render.resolution_x = scene.render.resolution_y = scene_def.resolution
    groups = [load_group(g, scene_def.uniform_role) for g in scene_def.groups]

    if scene_def.layout == "exploded":
        objs = build_exploded(*groups)
        view, margin, fill = ISO, 1.15, False
    else:
        x = 0.0
        for group, objs_ in zip(scene_def.groups, groups):
            orient(objs_, group.up)
            x += place(objs_, x) + mm(FLAT_LAY_GAP_MM)
        objs = [o for g in groups for o in g]
        view, margin, fill = ISO, 1.2, False
        if scene_def.layout == "flat-lay":
            # Lower and more frontal, so side-by-side parts do not hide
            # one another.
            view = Vector((0.35, -1.0, 0.45))
        if scene_def.layout == "section":
            lo, hi = combined_bbox(objs)
            for obj in objs:
                cut_half(obj, bbox_center(lo, hi), axis=1, keep_positive=True)
                set_material(obj, role_material(obj["role"]))
            view, margin, fill = Vector((0.0, -1.0, 0.15)), 1.1, True

    lo, hi = combined_bbox(objs)
    center, radius = bbox_center(lo, hi), bbox_radius(lo, hi)
    add_shadow_catcher(lo, hi)
    if fill:
        lighting(center, fill_dir=view, fill_radius=radius, fill_strength=CUT_FILL_STRENGTH)
    else:
        lighting(center)
    frame_camera(center, radius, view, margin=margin)
    return scene, objs


def run(name):
    scene_def = SCENES[name]
    print(f"== {name} ({scene_def.layout}, {scene_def.resolution}px)")
    scene, objs = build(scene_def)
    render(scene, name)
    # 30000 / 8000, not 60000 / 30000: the first full render pass put
    # site/public/renders + site/public/models at 25.2 MB against the 20 MB
    # budget (controller ruling, Task 8 brief). Lowering concept-*
    # resolution alone (tools/parts.py) does not touch this number, only
    # PNG size: it is the triangle ceiling that matters here, because
    # concept-* and rig-artificial-vagina each have exactly one large
    # single-shell solid (a cup body or the rig, 35k-66k raw triangles)
    # that planar dissolve alone cannot bring under 15000, so the 15000
    # ceiling was still collapse-decimating it every time; dropping to
    # 8000 measured ~1.5 MB off those 9 GLBs combined (13.3 -> 8.8 MB
    # totalled across all 13 models) without changing any part's
    # silhouette at the render's own on-screen size, and the hero
    # flower-low-* scenes keep the 30000 ceiling untouched (their two
    # largest solids, ~17.7k tris, mostly clear it already).
    export_glb(name, objs, max_tris=30000 if scene_def.resolution >= 2000 else 8000)


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for name in (args or sorted(SCENES)):
        run(name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
