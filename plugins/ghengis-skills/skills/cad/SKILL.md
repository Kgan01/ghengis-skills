---
name: cad
description: Use when the user wants to design a parametric 3D-printable part, mechanical bracket, enclosure, robot frame, sheet-metal panel, or any CAD model from a natural-language description. Calls the JARVIS build123d pipeline (Claude Max → build123d code → STEP/STL/3MF/DXF + topology sidecar) and verifies geometry via the bundled inspector. Cost is $0 when CLAUDE_MAX_ENABLED is set.
---

# CAD — parametric design from a description

When the user describes a CAD part (a bracket, enclosure, mount, lid, plate, holder, gear, robot link, sheet-metal panel, or any 3D-printable / engineering geometry), drive the JARVIS CAD pipeline and verify the result before reporting.

## When to use this skill

Trigger words and intents:
- "design me a…", "model a…", "make a part…", "generate a CAD…"
- explicit dimensions in mm/inches, hole patterns, tolerances
- requests for `.step`, `.stp`, `.stl`, `.3mf`, `.dxf`, `.glb`
- mechanical primitives: bracket, mount, enclosure, lid, standoff, gear, hinge, plate, panel, fixture
- robotics: URDF/SDF/SRDF descriptions (delegate to those skills if present)

Do **not** use for organic/aesthetic shapes from a reference image (use the TRELLIS / image-to-3D path instead) or for CAM toolpaths and FEA.

## Prerequisites

Working environment must satisfy:

1. JARVIS repo at `C:\Users\krist\OneDrive\Desktop\Jarvis` (adjust path if elsewhere).
2. Python env has `build123d` installed (`pip install build123d`).
3. `.env` has `CLAUDE_MAX_ENABLED=true` (uses the user's Claude Max OAuth — $0 cost).
4. Optional but recommended: `trimesh` for lightweight preview rendering.

If any of these fails, report the missing piece and stop. Do not silently fall back to a degraded path.

## The pipeline (what to actually do)

For every CAD request, run this exact sequence in order. Each step is a single Bash call from `apps/server`.

### 1. Generate via Claude Max + build123d

```python
import asyncio, pathlib, os
from dotenv import load_dotenv
load_dotenv(pathlib.Path('..') / '..' / '.env')
from tools.cad_tools import generate_parametric

PROMPT = """{verbatim user spec — dimensions, features, materials, tolerances}"""
MODEL_ID = "{short_slug_of_part_name}"  # e.g. 'pi4_mount', 'fieldy_lid', 'm5_washer'

async def go():
    result = await generate_parametric(
        prompt=PROMPT, model_id=MODEL_ID, exports=('stl', 'step')
    )
    for k, v in result.items():
        sz = f' ({os.path.getsize(v):,} B)' if isinstance(v,str) and v and os.path.exists(v) else ''
        print(f'  {k}: {v}{sz}')

asyncio.run(go())
```

Always include `'step'` in `exports` — it triggers the `scripts/step` canonical pipeline, which produces the GLB topology sidecar that the inspector needs.

### 2. Verify geometry via `cad_inspect`

Don't trust visual review for dimension correctness. Always run the inspector and report what it found vs the spec:

```python
import asyncio
from tools.cad_tools import CadInspect

async def go():
    res = await CadInspect()(step_path=r"<path from step 1>", facts=True)
    if res.success:
        for tok in res.output['tokens']:
            print('size:  ', tok['entryFacts'].get('size'))
            print('faces: ', tok['summary']['faceCount'])
            print('edges: ', tok['summary']['edgeCount'])
            print('bounds:', tok['summary']['bounds'])

asyncio.run(go())
```

Compare returned `size` vs the spec. If it deviates by more than 0.1 mm on any axis, the LLM probably misread the spec — flag this to the user and offer to regenerate with a more explicit prompt.

### 3. Show the user the result

Two paths depending on environment:

**With computer-use available** (preferred):
```bash
cmd.exe /c start "" "<path-to-model.stl>"
```
This opens the system's STL viewer (Windows 3D Viewer on Win11) — the user can rotate it themselves.

**Headless / want an inline preview**: use the trimesh + matplotlib renderer pattern:
```python
import trimesh, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
m = trimesh.load(STL_PATH)
normals = m.face_normals
light = np.array([0.5, -0.5, 1.0]); light = light/np.linalg.norm(light)
shade = np.clip(normals @ light, 0.2, 1.0)
# ... render via Poly3DCollection with shaded face colors
```
This gives proper hole/pocket visibility (matplotlib triangulation alone does not).

### 4. Open the artifact folder

```bash
explorer.exe "C:\Users\krist\.jarvis\cad\<MODEL_ID>\"
```

So the user has `source.py`, `gen_step.py`, `model.step`, `model.stl`, `.model.step.glb`, and any rendered previews at their fingertips.

## Build123d conventions the LLM must follow

When writing the prompt that goes to Claude Max via `generate_parametric`, include this rubric:

- All dimensions in **millimeters** unless the user says otherwise.
- Use **`BuildPart`** for solids, **`BuildSketch`** for 2D profiles.
- Place features with **`Locations(...)`** and `mode=Mode.SUBTRACT` for cavities/holes/cutouts.
- Use **`fillet(edges, radius)`** for rounds, **`chamfer(edges, distance)`** for chamfers.
- Filter edges with **`.filter_by(Axis.Z)`** for vertical edges, **`sort_by(Axis.Z)`** for top/bottom selection.
- The script must assign the final part to a variable named **`result`** at module scope.
- No file I/O, no `os.system`, no `subprocess`, no `eval/exec`. The AST validator will reject those.

## Iterative edits

If the user says "now add a snap-fit lid" or "make it 5 mm thicker", regenerate with a new `model_id` (e.g. `fieldy_lid` after `fieldy_pendant`) and reference the base part's dimensions in the new prompt. There is no edit-in-place yet — every iteration is a clean regeneration.

## Reporting

Tell the user:
1. **What dimensions came back from the inspector** vs what they asked for (truth, not visual review).
2. **Where the artifacts live** (`~/.jarvis/cad/<MODEL_ID>/`).
3. **What the build123d source looks like** (paste it inline — usually 10–25 lines).
4. **LLM round-trip time and cost** (always $0 when `CLAUDE_MAX_ENABLED=true`).

## Failure modes and quick fixes

| Symptom | Fix |
|---|---|
| `Claude CLI timed out (60s)` | Complex prompts can run 60–120 s. The helper now passes `timeout=180` by default; if you bypass it, pass `timeout=180` explicitly via `kwargs`. |
| `scripts/step output pair must use POSIX '/' separators` | Use `Path.as_posix()` for the target spec — already handled in `cad_tools.py`, but watch for it in direct `scripts/step` calls. |
| `CadSourceError: Forbidden import: X` | The LLM tried to import `subprocess`/`socket`/etc. Re-prompt with stricter instructions or trim what the LLM produced before re-running. |
| Inspector reports `missing_glb` | The STEP was made by a tool other than `scripts/step` — regenerate via `cad_generate_parametric` instead of raw `build123d.export_step()`. |

## Files this skill assumes exist

- `apps/server/tools/cad_tools.py` — `generate_parametric()`, `CadInspect`, `CadExport`, `CadStepPartsFind`.
- `apps/server/skills/upskill/cad/scripts/step/` — bundled canonical exporter (text-to-cad).
- `apps/server/skills/upskill/cad/scripts/inspect/` — bundled geometry inspector (text-to-cad).
- `apps/server/agents/registry.py` — `fabrication.cad_engineer` worker is wired to call these tools when the user goes through `JarvisOrchestrator.handle()` instead of using this skill directly.

## Notes

- The text-to-cad upstream (`earthtojake/text-to-cad`) is the source of the bundled `scripts/`. Don't fork them — just upgrade the in-tree copy when needed.
- For step.parts (off-the-shelf hardware lookup), use `cad_step_parts_find` — but the API host is currently unreachable; degrade gracefully.
- The bundled renderer (`scripts/render`) needs Playwright + vtk + Chromium (~425 MB). We deliberately skipped it; use trimesh + matplotlib or computer-use instead.
