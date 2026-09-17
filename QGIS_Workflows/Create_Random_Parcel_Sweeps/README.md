# Create Random Parcel Sweeps

Cinema 4D Python utility for creating one Sweep object per spline, with a randomized Rectangle height.

This script is useful for parcel boundaries, fences, curbs and similar architectural, topographic or GIS workflows.

## How to use

Example scene before running the script:

Select the `PARCEL_SPLINES` group first, then select `SWEEP_TEMPLATE` last while holding `Ctrl`.

### 1. Prepare the parcel splines

Place all parcel splines inside a group / Null object.

Example:

```text
PARCELS
├── Parcel_001
├── Parcel_002
├── Parcel_003
├── Parcel_004
└── Parcel_005

The script searches recursively inside the selected group.

2. Create a template Sweep

Create one Sweep object that will be used as the template.

The Sweep must contain a Rectangle as its first child:

SWEEP_TEMPLATE
└── Rectangle

Set the Rectangle width as desired.

The script will clone this Sweep for every parcel spline.

3. Select the objects in the correct order

This step is important.

First select the group containing the parcel splines.

Then, while holding Ctrl, select the template Sweep LAST.

The selection order must be:

1. Parcel group / Null
2. Template Sweep

The Sweep must be the last selected object.

4. Run the script

Run:

Create_Random_Parcel_Sweeps.py

A series of dialog boxes will ask for:

Minimum Rectangle height
Maximum Rectangle height
Random Seed

Example:

Minimum height: 160
Maximum height: 220
Random Seed: 12345

In the original workflow:

160 = 1.60 m
220 = 2.20 m
5. Result

The script creates one Sweep for every parcel spline.

Example:

Sweep_Parcel_001
├── Rectangle
└── Parcel_001

Sweep_Parcel_002
├── Rectangle
└── Parcel_002

Sweep_Parcel_003
├── Rectangle
└── Parcel_003

Each Rectangle receives a random height between the minimum and maximum values entered by the user.

Random Seed

The Random Seed controls the random distribution.

Using the same seed will reproduce the same result.

Example:

Seed 12345

will always generate the same random sequence.

Changing the seed:

12346

creates a different variation.

Important

The template Sweep must be selected last.

Correct:

PARCELS
SWEEP_TEMPLATE

Incorrect:

SWEEP_TEMPLATE
PARCELS

If the Sweep is not selected last, the script will not run correctly.

Compatibility

Tested with:

Cinema 4D 2023.1.2

Other Cinema 4D versions may also work but have not been tested.

Typical use cases

Useful for:

QGIS parcel exports
DXF parcel boundaries
Property boundaries
Fences
Curbs
Landscape boundaries
Architectural site models
Urban visualization workflows
GIS / topographic workflows
Undo

The script supports Cinema 4D Undo.

Use:

Ctrl + Z

to undo the generated Sweeps.

License

MIT