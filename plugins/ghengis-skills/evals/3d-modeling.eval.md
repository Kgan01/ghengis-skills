# 3D Modeling -- Evaluation

## TC-1: Design a Phone Stand Prompt
- **prompt:** "I want to 3D print a phone stand for my iPhone 15. Help me design it."
- **context:** User wants a printable phone stand. Skill should produce a detailed prompt with dimensions, constraints, and printability considerations.
- **assertions:**
  - Specifies function (hold phone at comfortable viewing angle)
  - Includes specific dimensions (base ~100mm, slot ~12mm wide for phone + case, angle 60-70 degrees)
  - Includes printability constraints (no overhangs >45 degrees, flat base for adhesion)
  - Specifies wall thickness (minimum 2mm for structural integrity)
  - Mentions material recommendation (PLA for rigid stand)
  - Output follows the prompt template: [Object] + [Style] + [Dimensions] + [Constraints]
- **passing_grade:** 4/6 assertions must pass

## TC-2: STL Mesh Quality Check
- **prompt:** "I downloaded an STL file and my slicer shows warnings about non-manifold edges. How do I fix it?"
- **context:** User has a broken STL file that won't slice properly.
- **assertions:**
  - Explains what non-manifold means (not watertight, edges not shared by exactly 2 triangles)
  - Recommends a mesh repair tool (Meshmixer, Netfabb, or Windows 3D Builder)
  - Provides the quick fix workflow: import -> Analysis/Inspector -> Auto Repair All -> export fixed STL
  - Advises re-importing the fixed STL into the slicer to verify warnings are gone
  - Does not suggest manually editing triangles as a first step
- **passing_grade:** 4/5 assertions must pass

## TC-3: Print Orientation for a Functional Hook
- **prompt:** "I'm printing a wall hook. It will bear weight pulling downward. How should I orient it?"
- **context:** Functional part where layer line direction determines strength.
- **assertions:**
  - Recommends printing upright so stress is perpendicular to layer lines (layers pulled together, not apart)
  - Warns against printing flat (stress parallel to layers = will snap at layer lines)
  - Addresses overhangs (the hook curve may need supports if >45 degrees)
  - Suggests placing supports on non-visible surfaces
  - Recommends higher infill (30%+) for structural strength
- **passing_grade:** 4/5 assertions must pass

## TC-4: Tolerance for Snap-Fit Parts
- **prompt:** "I'm designing a two-part box with a snap-fit lid. How much clearance do I need?"
- **context:** Multi-part print requiring precise tolerances.
- **assertions:**
  - Recommends 0.2-0.3mm clearance for sliding/snap fit (not zero clearance)
  - Mentions that FDM printers typically print holes slightly smaller than designed
  - Advises printing small test pieces first before committing to the full print
  - Specifies minimum wall thickness for the snap feature (1.2mm+ to flex without breaking)
  - Notes that tolerance varies by printer and material
- **passing_grade:** 4/5 assertions must pass

## TC-5: Vague Prompt Correction
- **prompt:** "Make me a desk organizer"
- **context:** User provides a vague prompt. Skill should either ask clarifying questions or generate a detailed, printable specification.
- **assertions:**
  - Does not generate a vague model description matching the vague input
  - Either asks clarifying questions (how many compartments, what items, dimensions) OR provides a detailed default specification
  - If providing a specification, includes specific dimensions (width, depth, height per compartment)
  - Includes printability constraints (wall thickness, flat base, no overhangs)
  - Follows the prompt template format: [Object] + [Style] + [Dimensions] + [Constraints]
- **passing_grade:** 3/5 assertions must pass
