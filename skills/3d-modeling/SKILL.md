---
name: 3d-modeling
description: Use when helping with 3D modeling, STL file quality, or 3D printing preparation -- covers mesh quality, support structures, printability considerations, and model optimization
---

# 3D Modeling for Printing

When helping with 3D modeling, STL file evaluation, or 3D printing preparation, follow this methodology for printable geometry, optimal orientation, and reliable prints.

## Core Concepts

### Image-to-3D Prompt Engineering

When generating 3D models from text or image descriptions, prompt quality directly determines printability.

**Effective Prompt Structure**
```
[Object] + [Style] + [Details] + [Constraints]

Good: "Phone stand, minimalist design, angled at 60 degrees, fits iPhone 14, flat base for stability"
Bad: "Make me a phone stand"
```

**Key Elements to Specify**
- **Function**: What does it do? (hold, clip, mount, organize)
- **Dimensions**: Specific measurements (holds 15mm pen, 100mm wide base)
- **Style**: Minimalist, organic, geometric, industrial, steampunk
- **Constraints**: Printable (no overhangs >45 deg), solid/hollow, wall thickness
- **Material intent**: PLA (rigid), TPU (flexible), PETG (strong)

**Example Prompts**
```
"Desk organizer with 3 compartments:
 - Front: 80mm wide, 50mm deep (for pens)
 - Back left: 60mm square (for sticky notes)
 - Back right: 40mm diameter cylinder (for scissors)
 - 3mm wall thickness, flat bottom, no overhangs"

"Headphone stand, Y-shaped, 200mm tall,
 - 100mm wide curved top (to hold headband),
 - 150mm diameter circular base,
 - 5mm wall thickness, minimalist design,
 - optimized for PLA printing (no supports)"

"Spiral vase, 150mm tall, 80mm diameter base,
 - Tapers to 60mm at top,
 - 1mm wall thickness (single wall print),
 - Vase mode compatible, organic curves"
```

**Printability Modifiers**
- "No overhangs greater than 45 degrees"
- "Flat base for adhesion"
- "Self-supporting geometry"
- "3mm minimum wall thickness"
- "Chamfered edges" (easier to print than sharp edges)
- "Avoid thin vertical walls" (risk of warping)

### STL Mesh Quality

**What is STL?**
- File format: Surface mesh of triangles
- No color, no texture, just geometry
- Industry standard for 3D printing

**Triangle Count**

| Range | Quality | Notes |
|-------|---------|-------|
| 1k-10k | Low-poly | Fast, but faceted/angular |
| 10k-100k | Medium | Good balance for most prints |
| 100k-1M+ | High-poly | Smooth curves, large file size |

Rule: Use the lowest count that looks smooth. File size matters for slicers.

**Manifold Geometry (CRITICAL)**
- **Manifold**: Watertight, no holes, each edge shared by exactly 2 triangles
- **Non-manifold**: Holes, intersecting faces, naked edges
- **Why it matters**: Non-manifold geometry = slicer errors = failed prints

**Common Mesh Issues**
- **Holes**: Missing triangles (surface has gaps)
- **Inverted normals**: Face pointing wrong direction (inside-out)
- **Intersecting faces**: Two surfaces occupy same space
- **Naked edges**: Edge only attached to 1 triangle (not 2)
- **Duplicate vertices**: Multiple points at same location

**Mesh Repair Tools**

| Tool | Cost | Notes |
|------|------|-------|
| Meshmixer | Free | Auto-repair, easy to use |
| Netfabb | Free online | Powerful repair |
| Blender | Free | Manual control, learning curve |
| Windows 3D Builder | Free | Auto-repair on import |

### Manifold Geometry Validation

**Tests for Manifold**
1. **Watertight test**: Could it hold water? (no holes)
2. **Edge count**: Every edge shared by exactly 2 faces
3. **Normal consistency**: All normals point outward (not mixed)
4. **No self-intersection**: Surfaces don't pass through each other

**How to Check**
- Most slicers (Cura, PrusaSlicer): Import STL, look for warnings
- Meshmixer: Analysis -> Inspector (red areas = problems)
- Netfabb: Import -> Automatic repair -> Displays issues
- Windows 3D Builder: Import (auto-repairs, shows message if fixed)

**Quick Fix Workflow**
```
1. Import STL into Meshmixer
2. Analysis -> Inspector
3. Auto Repair All
4. Export -> STL (fixed)
```

### Print Orientation Optimization

**Why Orientation Matters**
- **Strength**: Layers bond weakest direction (avoid stress along layer lines)
- **Surface quality**: Bottom = smooth (bed contact), top = smooth (solid layers), sides = layer lines visible
- **Supports**: Minimize overhangs >45 deg to reduce support material
- **Print time**: Fewer layers = faster (orient to minimize Z height)

**Orientation Guidelines**

| Part Type | Recommendation | Reason |
|-----------|---------------|--------|
| **Functional parts** | Stress perpendicular to layers | Layers pulled together, not apart |
| **Aesthetic parts** | Visible surfaces flat on bed or on top | Smooth finish |
| **Overhangs** | Rotate to minimize >45 deg angles | Self-supporting geometry |
| **All parts** | Flat base on bed | Better adhesion, stability |

**Examples**
```
Phone stand:
- Print upright (stress perpendicular to layers)
- Angle may require support for back lip

Miniature figure:
- Print at 45 deg angle (reduces overhangs on arms/weapons)
- Smaller layers = more detail (0.1mm layer height)

Vase:
- Print upright in vase mode (spiralized outer contour, no top layers)

Threaded lid:
- Print threads vertically (perpendicular to layers = stronger)
```

### Support Structure Planning

**When Supports Are Needed**
- Overhangs >45 deg (60 deg possible with good cooling)
- Bridges >10mm without bottom layer
- Islands (floating geometry with nothing below)

**Support Types**

| Type | Description | Best For |
|------|-------------|----------|
| **Grid** | Standard lattice | General purpose, easy removal |
| **Tree** | Organic branches | Less material, complex overhangs |
| **Touching buildplate** | Only from bed up | Less material, less scarring |
| **Everywhere** | From bed and model | Complex internal overhangs |

**Support Settings (Cura Example)**
```
Support density:    10-15% (less = easier removal)
Support Z distance: 0.2mm (layer height x 2-3)
Support interface:  Enabled (smoother bottom, easier removal)
Support pattern:    Zigzag (fast, easy removal)
```

**Strategy**: Supports always leave scars. Place them on non-visible surfaces. Rotate the model to minimize overhangs before adding supports.

### Dimension Specification

**Design for Tolerances**
- Holes: Print 0.2-0.3mm smaller (expand with drill if needed)
- Pegs: Print 0.2-0.3mm smaller than hole (sliding fit)
- Threads: Add 0.1-0.2mm clearance
- Snap fits: Test small versions first (tolerance varies by printer)

**Wall Thickness**

| Purpose | Thickness | Notes |
|---------|-----------|-------|
| Minimum | 0.8mm | 2x nozzle width for 0.4mm nozzle |
| Light-duty | 1.2mm | 3 walls |
| Standard | 2.0mm | 5 walls |
| Heavy-duty | 2.8mm+ | 7+ walls |

**Feature Size Limits**
- Minimum detail: 0.4mm (nozzle width, smaller may not print)
- Minimum hole: 1mm (smaller = drill after)
- Text: 3mm+ tall for readability (embossed or debossed)

**Clearances**

| Fit Type | Gap |
|----------|-----|
| Sliding fit | 0.2mm |
| Loose fit | 0.5mm |
| Press fit | -0.1mm (interference, requires force) |

**Common Object Measurements**
```
Phone stand:
- Base: 100mm x 80mm (stable footprint)
- Height: 120mm (adjustable angle)
- Slot: 12mm wide (fits phone + case)
- Angle: 60-70 deg (comfortable viewing)

Pen holder:
- Diameter: 18-20mm (holds most pens)
- Depth: 60-80mm (pens don't fall out)
- Wall: 2mm (rigid but not heavy)

Cable clip:
- Inner diameter: 6mm (for 5mm cable with tolerance)
- Grip: 180-270 deg wrap (holds without force)
- Wall: 1.5mm (flexible enough to snap on)
```

## Patterns and Procedures

### Image-to-3D Generation Workflow

```
1. Clarify intent:
   - What's the object's function?
   - What are the constraints? (size, printability)

2. Craft prompt:
   - Object + style + dimensions + constraints
   - "Minimalist phone stand, 60 deg angle, 100mm base, no overhangs"

3. Generate (via AI image-to-3D service)

4. Evaluate result:
   - Is geometry manifold? (watertight?)
   - Are there printable overhangs?
   - Are dimensions correct?

5. Iterate or repair:
   - Refine prompt if geometry wrong
   - Repair mesh if non-manifold
   - Adjust orientation in slicer
```

### STL Quality Check Workflow

```
1. Import STL into slicer (Cura, PrusaSlicer)
2. Check for warnings:
   - "Non-manifold edges" -> Repair needed
   - "Model has holes" -> Repair needed
   - No warnings -> Likely good

3. If warnings, open in Meshmixer:
   - Analysis -> Inspector
   - Auto Repair All
   - Export fixed STL

4. Re-import into slicer:
   - Verify no warnings
   - Proceed to slicing
```

### Print Orientation Process

```
1. Import model into slicer
2. Evaluate current orientation:
   - Where are overhangs? (red areas in Cura)
   - Where is stress in use? (avoid parallel to layers)
   - Which surfaces need to be smooth?

3. Rotate model:
   - Minimize overhangs (self-supporting <45 deg)
   - Stress perpendicular to layers
   - Visible surfaces flat or on top

4. Check supports:
   - Enable supports if overhangs >45 deg
   - Place on non-visible surfaces if possible

5. Verify base:
   - Flat, stable contact with bed
   - Add brim if small contact area
```

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| **Vague prompts** | Generic, not printable, wrong size | Specify function, dimensions, constraints |
| **Ignoring non-manifold** | Slicer warnings, print fails | Always check manifold, repair before slicing |
| **Wrong orientation** | Hook printed flat = snaps at layer line | Print upright (stress perpendicular to layers) |
| **Over-supporting** | 50% of print is support = waste | Rotate to minimize overhangs, use "touching buildplate" |
| **Tolerances too tight** | Parts don't fit (10mm hole prints as 9.8mm) | Add 0.2-0.3mm clearance |
| **Walls too thin** | 0.5mm wall doesn't print or is fragile | Minimum 0.8mm (2x nozzle width) |

## Quick Reference

### Printable Overhang Angles

```
0-45 deg:  Self-supporting (no supports needed)
45-60 deg: Possible (depends on cooling, may sag)
60-70 deg: Needs supports (will fail without)
70-90 deg: Heavy supports required
```

### Common Print Settings (PLA)

```
Layer height: 0.2mm (standard), 0.1mm (detail), 0.3mm (draft)
Nozzle temp:  200-220 C
Bed temp:     60 C
Print speed:  50mm/s (standard), 30mm/s (detailed)
Infill:       15% (standard), 5% (light), 30%+ (strong)
```

### Tolerance Chart (0.4mm Nozzle)

```
Sliding fit: +0.2mm clearance
Loose fit:   +0.5mm clearance
Press fit:   -0.1mm (interference)
Threads:     +0.15mm clearance
Snap fit:    Test (varies by geometry)
```

### File Formats

```
STL:  Standard (triangles, no color)
OBJ:  Includes color/texture (most slicers ignore)
3MF:  Modern (includes color, settings, multi-part)
AMF:  Compressed (less common)

Best: STL for single-color, 3MF for multi-color/settings
```

### Prompt Template

```
[Object], [style], [dimensions], [constraints]

Example:
"Cable organizer, 5 channels, 120mm wide x 80mm deep x 20mm tall,
 3mm wall thickness, flat base, no overhangs, minimalist"
```

## Checklists

### Before Generating 3D Model
- [ ] Define function (what does it do?)
- [ ] Specify dimensions (exact measurements)
- [ ] Identify constraints (printability, material, orientation)
- [ ] Choose style (minimalist, organic, geometric)
- [ ] Write detailed prompt (object + style + dimensions + constraints)

### After Receiving STL File
- [ ] Import into slicer (Cura, PrusaSlicer)
- [ ] Check for errors (non-manifold, holes, inverted normals)
- [ ] If errors, repair (Meshmixer auto-repair)
- [ ] Verify dimensions (scale if needed)
- [ ] Check file size (<50MB ideal, >100MB = slow)

### Optimizing Print Orientation
- [ ] Identify stress direction (functional parts)
- [ ] Rotate so stress perpendicular to layers (stronger)
- [ ] Minimize overhangs (self-supporting <45 deg)
- [ ] Place visible surfaces flat or on top (smooth finish)
- [ ] Verify flat base on bed (stable adhesion)

### Planning Supports
- [ ] Check overhang angles (red = needs support in Cura)
- [ ] Rotate to minimize supports (if possible)
- [ ] Enable supports (touching buildplate preferred)
- [ ] Adjust density (10-15% for easy removal)
- [ ] Enable support interface (smoother finish)
- [ ] Verify support removal access (can you reach them?)

### Validating Dimensions
- [ ] Critical dimensions specified (holes, pegs, clearances)
- [ ] Tolerances added (0.2-0.3mm for fits)
- [ ] Wall thickness adequate (min 0.8mm, prefer 1.2mm+)
- [ ] Feature sizes printable (min 0.4mm detail)
- [ ] Test fit if multi-part (print test pieces first)

### Before Slicing
- [ ] Model is manifold (watertight, no errors)
- [ ] Orientation optimized (strength + aesthetics)
- [ ] Supports planned (minimal, strategic)
- [ ] Dimensions verified (to-spec with tolerances)
- [ ] Material selected (PLA, PETG, TPU)
- [ ] Print settings chosen (layer height, infill, speed)
