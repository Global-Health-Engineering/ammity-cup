"""Which solids make up each render, what they are, and how they sit.

Pure Python (no numpy) so Blender's bundled interpreter can import it.
Solid indices refer to build/meshes/<slug>/<stem>/index.json written by
tools/step_to_mesh.py, which preserves the STEP file's own solid order.

A Group is a set of STEP files that share one coordinate frame and can
therefore be shown assembled. Parts from files whose frames differ are
never forced together (that would be a made-up assembly); a scene lays
such groups side by side and its caption says so.
"""
import os
from dataclasses import dataclass

# Scene-linear Principled BSDF base colours (Standard view transform, so
# displayed sRGB ~ linear^(1/2.2)). Nothing lighter than 0.62, or the part
# loses its silhouette on the site's near-white card (--bg-2 #f6f7f9);
# the same limit 3DPLAM's renders learned. One colour per role in EVERY
# render, so a reader who learns "magenta is the closing mechanism" in one
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
class Group:
    steps: tuple
    up: str
    default_role: str = "body"
    roles: dict = None
    exclude: tuple = ()
    mirror: tuple = None


@dataclass(frozen=True)
class Scene:
    name: str
    groups: tuple
    layout: str
    caption: str
    resolution: int = 1000
    uniform_role: str = None


def _hw(slug, stem):
    return f"hardware/{slug}/step/{stem}.step"


FLOWER_LOW = Group(
    steps=(_hw("flower-low", "flower-cup-withrim-part"),),
    up="+y",
    roles={0: "body", 1: "body", 2: "body", 3: "body", 4: "mechanism", 5: "mechanism"},
)
FLOWER_HIGH = Group(steps=(_hw("flower-high", "flower-cup-withrim-higher"),), up="+y")
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
    ),
    "duckbill": (
        Group(steps=(_hw("duckbill", "duckbill-half-withrim"),), up="+y", exclude=(1,),
              mirror=("z", 0.0)),
    ),
    "balloon": (
        Group(steps=(_hw("balloon", "menstrual-cup-medium-without-balloon"),
                     _hw("balloon", "balloon-pipe")), up="+y"),
    ),
    "extraction-valve": (
        Group(steps=(_hw("extraction-valve", "menstrual-cup-valve"),), up="+y"),
        Group(steps=(_hw("extraction-valve", "cup-valve-button"),), up="+z", default_role="mechanism"),
    ),
}

CONCEPT_CAPTIONS = {
    "flower-low": "Flower Low: five petals at the opening, pulled closed by strings through the stem.",
    "flower-high": "Flower High: the same mechanism with the petal bases nearer the rim.",
    "twister": "Twister: top and bottom sections; the thin membrane skin that joins them is shown beside them.",
    "umbrella": "Umbrella: cup body, the umbrella insert, and its silicone housing, shown side by side.",
    "drawstring": "Drawstring: cup body with the string channels; the folded lid is moulded flat and not shown.",
    "duckbill": "Duckbill: moulded as two halves and joined; shown as the mirrored pair.",
    "balloon": "Balloon: cup body and bulb pipe; the balloon membrane exists only as its mould.",
    "extraction-valve": "Extraction valve: cup body and valve button, shown side by side. Untested concept.",
}

SCENES = {}
for slug, groups in CONCEPT_GROUPS.items():
    SCENES[f"concept-{slug}"] = Scene(
        name=f"concept-{slug}", groups=groups,
        layout="assembled" if len(groups) == 1 else "flat-lay",
        caption=CONCEPT_CAPTIONS[slug])

SCENES.update({
    "flower-low": Scene("flower-low", (FLOWER_LOW,), "assembled",
                        "Flower Low, the design flown on the parabolic flights.", resolution=2000),
    "flower-low-section": Scene("flower-low-section", (FLOWER_LOW,), "section",
                                "Cut through Flower Low: petals and the string channels in the stem.",
                                resolution=2000),
    "flower-low-vs-high": Scene("flower-low-vs-high", (FLOWER_LOW, FLOWER_HIGH), "flat-lay",
                                "Flower Low (left) and Flower High (right).", resolution=2000,
                                uniform_role="body"),
    "flower-low-mould": Scene("flower-low-mould", (FLOWER_LOW_MOULD, FLOWER_LOW), "exploded",
                              "The printed mould for Flower Low, opened at its parting plane, with the cast cup.",
                              resolution=2000),
    "rig-artificial-vagina": Scene(
        "rig-artificial-vagina",
        (Group(steps=(_hw("artificial-vagina", "parabolicflight-vagina"),), up="+z", default_role="rig"),),
        "assembled", "The artificial vagina test model, cast in silicone from a printed mould."),
})
