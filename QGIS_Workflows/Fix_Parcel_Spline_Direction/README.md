# Fix Parcel Spline Direction

Cinema 4D Python utility for correcting the point direction of closed parcel splines.

This script is designed for GIS, DXF, topographic and architectural workflows where imported parcel splines may not all share the same point direction.

It is particularly useful before generating surfaces for applications such as D5 Render Scatter.

---

## What it does

Closed splines can have different point directions.

Depending on the direction of their points, a generated surface may face:

```text
+Y

or:

-Y

This can become a problem when another application uses the surface normals.

For example, in D5 Render, vegetation using Along Normal may be generated in the wrong direction if the source surface faces downward.

This script automatically analyses the selected parcel splines and corrects their direction so that they are consistently oriented toward +Y.

Important

The script does not move, flatten or modify the shape of the parcel splines.

The original:

X
Y
Z

coordinates are preserved.

Only the order of the spline points is reversed when necessary.

This means a parcel following terrain elevation will keep exactly the same elevation after processing.

Required hierarchy

This script is designed to work with independent editable spline objects contained inside a Null / group.

Recommended structure:

PARCEL_SPLINES
├── Parcel_001
├── Parcel_002
├── Parcel_003
├── Parcel_004
└── Parcel_005

The splines should be independent editable spline objects.

They should not depend on a master object or another generated hierarchy.

Important limitation

For best results, use the script on a clean group containing independent parcel splines.

Recommended:

PARCEL_SPLINES
├── Spline_001
├── Spline_002
├── Spline_003
└── Spline_004

Not recommended:

MASTER_OBJECT
└── Generated_Splines
    ├── Spline_001
    ├── Spline_002
    └── Spline_003

or other setups where the splines depend on a master object, generator or procedural hierarchy.

The script is intended primarily for editable spline geometry imported from workflows such as QGIS / DXF.

How to use
1. Prepare the splines

Place all parcel splines inside a single Null / group.

Example:

PARCEL_SPLINES
├── Parcel_001
├── Parcel_002
├── Parcel_003
├── Parcel_004
└── Parcel_005

The splines should be closed whenever they represent parcel boundaries.

2. Select the group

Select only the group containing the parcel splines.

Example:

PARCEL_SPLINES

You do not need to select the individual splines.

The script searches recursively inside the selected group.

3. Run the script

Run:

Fix_Parcel_Spline_Direction.py

No additional settings are required.

4. Automatic analysis

For every closed spline, the script analyses the point direction using its projection on the XZ plane.

If the spline is already oriented toward:

+Y

it is left unchanged.

If the spline is oriented toward:

-Y

the point sequence is reversed automatically.

Result

Example before processing:

Parcel_001 → +Y
Parcel_002 → -Y
Parcel_003 → +Y
Parcel_004 → -Y

After processing:

Parcel_001 → +Y
Parcel_002 → +Y
Parcel_003 → +Y
Parcel_004 → +Y

The geometry remains in exactly the same position.

Bézier splines

The script also attempts to preserve Bézier spline behavior.

When a Bézier spline direction is reversed, the left and right tangents are exchanged accordingly.

This helps preserve the original spline shape.

Existing generators

To avoid accidentally modifying already processed geometry, the script ignores splines contained inside:

Sweep
Loft
Extrude

It is therefore recommended to run this script before generating Loft or Sweep objects.

Recommended workflow

A typical GIS / Cinema 4D workflow can be:

QGIS
↓
DXF Export
↓
Cinema 4D
↓
Parcel Splines
↓
Fix Parcel Spline Direction
↓
Create Parcel Lofts
↓
Export / LiveSync
↓
D5 Render Scatter

This ensures that generated parcel surfaces have a consistent orientation before being used as vegetation or scatter zones.

D5 Render use case

This script was originally created to solve a Scatter orientation problem in D5 Render.

When parcel surfaces were generated with inconsistent directions, using:

Along Normal = 1

could send vegetation downward on some surfaces.

Correcting the spline direction before creating the surfaces ensures that the resulting geometry is consistently oriented toward +Y.

Closed splines

The script is intended primarily for closed parcel boundaries.

Open splines are skipped.

Very small or degenerate shapes that cannot provide a reliable orientation in XZ projection may also be ignored.

Undo

The script supports Cinema 4D Undo.

Use:

Ctrl + Z

to restore the original spline directions after running the script.

Report

After processing, the script displays a report showing:

Number of splines analysed
Number of splines corrected
Number of segments reversed
Number of segments ignored

The report also confirms that the original X / Y / Z coordinates were not modified.

Compatibility

Tested with:

Cinema 4D 2023.1.2

Other Cinema 4D versions may also work but have not been tested.

Typical use cases
QGIS parcel exports
DXF parcel boundaries
GIS workflows
Topographic workflows
Architectural site models
Property boundaries
Landscape planning
D5 Render Scatter preparation
Surface normal preparation
Large urban visualization scenes
Recommended file structure
C4D-ArchViz-Workflow-Tools/
└── QGIS_Workflows/
    └── Fix_Parcel_Spline_Direction/
        ├── Fix_Parcel_Spline_Direction.py
        └── README.md

Always save your Cinema 4D scene before running geometry-processing scripts on important production files.

For testing, working on a copy of the scene is recommended.

License

MIT

