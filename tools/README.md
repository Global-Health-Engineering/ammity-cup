# tools

Every derived artifact in this repository regenerates from these scripts.
No figure is a one-off screenshot.

| Script | Regenerates |
|---|---|
| `stl_units.py` | STL geometry primitives (library) |
| `verify_units.py` | CI gate, fails if any STL is not in millimetres |
| `verify_scope.py` | CI gate, fails if a tracked file is out of scope (thesis, questionnaires, training slides, OSHWA artwork) |
| `verify_copy.py` | CI gate, fails if banned certification/safety phrasing reaches the docs or the built site |
| `verify_privacy.py` | CI gate, fails if participant names, personal paths or email addresses reach the docs or the built site |
| `rename.py` | The old-to-new file-name mapping in [`../hardware/README.md`](../hardware/README.md#rename-map) (library) |
| `step_to_mesh.py` | Meshes converted from the STEP files, input to `render_parts.py` |
| `parts.py` | The parts list walked by `step_to_mesh.py` and `render_parts.py` (library) |
| `render_parts.py` | `site/public/renders/*.png` and `site/public/models/*.glb` (requires Blender) |

## CI

```bash
pip install -r requirements.txt
python3 -m pytest tools/tests -v
```

## Renders

Rendering is not run in CI; it is a local, one-off step whenever the STEP files change.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-render.txt
.venv/bin/python tools/step_to_mesh.py
blender --background --python tools/render_parts.py
```
