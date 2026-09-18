# Assign Materials By Object Groups

Cinema 4D Python utility for assigning materials to objects in groups, following the Object Manager order from top to bottom.

This script is useful for large scenes where many objects need to be grouped visually or prepared for downstream workflows such as D5 Render, GIS visualization or architectural scene organization.

---

## What it does

The script:

- Reads the selected objects in Cinema 4D
- Follows the Object Manager order from **top to bottom**
- Groups objects by a user-defined quantity
- Creates one Cinema 4D Standard material per group
- Assigns the same material to all objects inside that group
- Creates a new Texture Tag if necessary
- Reuses the first existing Texture Tag when one is already present
- Supports Cinema 4D Undo

Example:

```text
Object_001
Object_002
Object_003
Object_004
Object_005
Object_006

If you enter:

3 objects per material

the result will be:

Object_001 → MAT_SCATTER_001
Object_002 → MAT_SCATTER_001
Object_003 → MAT_SCATTER_001

Object_004 → MAT_SCATTER_002
Object_005 → MAT_SCATTER_002
Object_006 → MAT_SCATTER_002
Supported object types

The script is designed to work with many Cinema 4D object types, including:

Polygon Objects
Loft
Sweep
Extrude
Primitives
Instances
Generators
Imported geometry
GLTF / FBX objects
Nested object hierarchies

Null objects are used only as hierarchy containers and are not assigned materials directly.

How to use
1. Select your objects

You can select:

One object
Multiple objects
A complete Null / group
Several groups

Example:

BUILDINGS
├── Building_001
├── Building_002
├── Building_003
├── Building_004
└── Building_005

You can simply select:

BUILDINGS

The script will search inside the group automatically.

2. Run the script

Run:

Assign_Materials_By_Object_Groups.py

A dialog box will ask:

Nombre d'objets par matériau

Enter the number of objects that should share the same material.

Example:

10
3. Result

The script creates materials named:

MAT_SCATTER_001
MAT_SCATTER_002
MAT_SCATTER_003
...

Each material receives a random color to make the groups easy to identify visually.

Object Manager order

Objects are processed according to their order in the Cinema 4D Object Manager.

The order is:

TOP
↓
Object_001
Object_002
Object_003
Object_004
Object_005
↓
BOTTOM

This means the first group receives the first material, the next group receives the second material, and so on.

This is particularly useful when the objects are already organized sequentially in the hierarchy.

Null groups

Null objects are treated only as containers.

Example:

GROUP
├── Object_001
├── Object_002
├── Object_003
└── Object_004

The GROUP Null itself will not receive a material.

Only its children will be processed.

Existing Texture Tags

If an object already contains a Texture Tag, the script reuses the first Texture Tag found and replaces its material.

If no Texture Tag exists, the script creates one automatically.

Typical use cases

Useful for:

Large architectural scenes
Archicad imports
QGIS / GIS workflows
Parcel visualization
Road geometry
GLTF / FBX imports
D5 Render preparation
Scatter zone organization
Scene segmentation
Urban visualization
Material grouping
Large object hierarchies
D5 Render use case

One useful workflow is to assign one material to groups of objects before sending the scene to D5 Render.

Example:

1300 parcel objects
↓
10 objects per material
↓
130 materials
↓
Use materials as control groups in D5

This makes it easier to control large numbers of objects without managing each object individually.

Random colors

The script creates materials with random colors.

This is intentional.

The colors make it easy to identify the different object groups visually inside Cinema 4D.

The random distribution is generated from a fixed seed, so the same script settings produce a reproducible color sequence.

Undo

The script supports Cinema 4D Undo.

Use:

Ctrl + Z

to undo the material assignment and created Texture Tags / materials.

Compatibility

Tested with:

Cinema 4D 2023.1.2

Other Cinema 4D versions may also work but have not been tested.

Important notes

The script works at the object level.

It does not currently assign materials to:

Polygon selections
Individual faces
Edges
Points

A future version may include a dedicated Polygon Face mode.

Recommended workflow
Select objects or group
↓
Run script
↓
Choose objects per material
↓
Materials are created automatically
↓
Objects are assigned from top to bottom
↓
Export / LiveSync to D5 or continue working in C4D
Recommended folder structure
C4D-ArchViz-Workflow-Tools/
└── Object_Management/
    └── Assign_Materials_By_Object_Groups/
        ├── Assign_Materials_By_Object_Groups.py
        └── README.md
Warning

Always save your scene before running batch-processing scripts on important production files.

For large scenes, it is recommended to test the script on a copy first.

License

MIT