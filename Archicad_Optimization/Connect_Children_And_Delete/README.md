# Connect Children And Delete

Cinema 4D Python utility designed to optimize heavy imported architectural scenes.

The script connects all objects contained inside each selected parent group using Cinema 4D's **Connect Objects + Delete** command.

## Main use case

This tool is particularly useful when an imported Archicad scene is organized into groups based on materials.

Example:

```text
CONCRETE
├── Object_001
├── Object_002
├── Object_003
└── Object_004

GLASS
├── Object_005
├── Object_006
└── Object_007

WOOD
├── Object_008
├── Object_009
└── Object_010

After running the script on these groups, the geometry inside each material group is connected into a single object.

Conceptually:

CONCRETE
└── Connected_Concrete

GLASS
└── Connected_Glass

WOOD
└── Connected_Wood

This can significantly reduce the number of objects in large architectural scenes while preserving a logical material-based organization.

Why use it?

Large Archicad imports can contain hundreds or thousands of individual objects.

When the hierarchy is already organized by material, connecting the objects inside each material group can:

Reduce the total number of scene objects
Simplify the Object Manager
Make large architectural scenes easier to manage
Improve scene preparation before export or rendering
Preserve a logical organization based on materials
How to use
Organize or identify the parent groups containing objects that should be connected.
Select one or more parent Null objects.
Run the script.
The children of each selected group are connected using Connect Objects + Delete.
Important

The script processes each selected parent group separately.

For best results, use it on groups that already represent a logical category, such as a material group.

Warning

The script uses Cinema 4D's:

Connect Objects + Delete

The original child objects are therefore deleted after the connected object is created.

Always save your scene before processing large hierarchies.

Compatibility

Tested with:

Cinema 4D 2023.1.2
Typical workflow
Archicad
↓
Import into Cinema 4D
↓
Objects grouped by material
↓
Connect Children And Delete
↓
Reduced object count
↓
Cleaner scene for rendering / export
