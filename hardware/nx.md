# Source CAD (Siemens NX)

The design was modelled in **Siemens NX 2406**. The shipped STEP files were exported from **NX 2406.3002 on 2026-09-08**; both facts are recorded in the STEP file headers themselves, for example:

```
FILE_NAME(
/* time_stamp */ '2026-09-08T16:13:29+02:00',
/* originating_system */ 'SIEMENS PLM Software NX2406.3002',
```

## No native NX files in this repository

The native NX part files (`.prt`) are not published here: they embed local file-system paths from the author's machine. STEP is the only editable format this repository ships.

## The editable format

STEP (AP214, millimetres) is the editable format and opens in any B-rep CAD tool, for example **NX**, **FreeCAD**, **Onshape** or **Fusion**. The shipped STEP files declare `SI_UNIT(.MILLI.,.METRE.)`; a re-export that does not set millimetres explicitly can silently change the scale.

## Regenerating the renders

The renders under `site/public/renders/` are generated from the STEP files, not from NX, by [`../tools/README.md`](../tools/README.md)'s `step_to_mesh.py` (converts each STEP file to a mesh) and `render_parts.py` (renders the meshes to the images used on the site).

Each script documents its own run command and requirements in its module docstring.
