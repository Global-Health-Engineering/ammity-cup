# NX source CAD

The source CAD for every part in [`README.md`](README.md) is **Siemens NX 2406**. The shipped STEP files were exported from **NX 2406.3002 on 2026-09-08**; both facts are recorded in the STEP file headers themselves, for example:

```
FILE_NAME(
/* time_stamp */ '2026-09-08T16:13:29+02:00',
/* originating_system */ 'SIEMENS PLM Software NX2406.3002',
```

## Opening the native files

Open a `.prt` file from any `nx/` folder in **NX 2406 or later**. Mould parts are separate `.prt` files from the cast-part `.prt` files, for example `flower_cup_withrim_part_m.prt` (the cup) and `flower_cup_withrim_mold_m.prt` (the mould). If you edit a part, keep the original file name so it stays traceable to the thesis and to [`README.md`](README.md#rename-map).

## Re-exporting STEP

If you change a `.prt` file and need a new STEP export, export it as **AP214**, with units set to **millimetres**. The shipped STEP files declare `SI_UNIT(.MILLI.,.METRE.)`; a re-export that does not set millimetres explicitly can silently change the scale.

## Without NX

The shipped STEP files are a full B-rep and can be opened and edited in any STEP-capable CAD tool, for example **FreeCAD**, **Onshape** or **Fusion**. The native `.prt` files require NX.

## Regenerating the renders

The renders under `site/public/renders/` are generated from the STEP files, not from NX, by [`../tools/README.md`](../tools/README.md)'s `step_to_mesh.py` (converts each STEP file to a mesh) and `render_parts.py` (renders the meshes to the images used on the site).

Each script documents its own run command and requirements in its module docstring.
