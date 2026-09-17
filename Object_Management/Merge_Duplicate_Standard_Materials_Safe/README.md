# Merge Duplicate Standard Materials Safe

Cinema 4D Python utility for safely merging duplicated Standard materials.

The script is designed for heavy architectural and archviz scenes where duplicated materials can accumulate after imports, copy/paste operations or scene merging.

## What it does

The script searches for Cinema 4D Standard materials that belong to the same material family.

Cinema 4D duplicate suffixes are automatically ignored when comparing names.

Examples:

```text
BETON
BETON.1
BETON.2
BETON (1)
BETON(2)
BETON.1 (2)

These names are considered part of the same material family.

Extra spaces are also normalized.

Example:

Isolation - Panneau rigide bleu
Isolation  -  Panneau rigide bleu
Isolation - Panneau rigide bleu 

are treated as the same base name.

Safe comparison

Materials are NOT merged based on their name alone.

Before merging, the script compares:

Enabled / disabled material channels
Material parameters
Colors
Channel values
Shaders
Texture assignments
Texture paths
Shader parameters
Sub-shaders

If any detected difference exists, the materials are kept separate.

Example

These materials can be merged:

BETON

Color: ON
Texture: beton.jpg
Bump: ON
Bump texture: beton_bump.jpg
Bump strength: 20%

and:

BETON.1

Color: ON
Texture: beton.jpg
Bump: ON
Bump texture: beton_bump.jpg
Bump strength: 20%

Result:

BETON

The duplicate material is removed and all Texture Tags using it are redirected to the material that is kept.

These materials will NOT be merged:

BETON
Bump strength: 20%

and:

BETON.1
Bump strength: 35%

They share the same base name but contain different values.

How to use
Open the Cinema 4D scene you want to clean.
Save the scene before running the script.
Open the Cinema 4D Script Manager.
Run:
Merge_Duplicate_Standard_Materials_Safe.py
No object or material selection is required.
The script scans all Standard materials in the current document.
A confirmation window appears before any duplicate material is deleted.
Confirm the operation.

The script then:

Redirects Texture Tags to the material that will be kept.
Removes only materials detected as true duplicates.
Keeps materials that contain different settings.
Displays a report when the operation is complete.
Undo

The script supports Cinema 4D Undo.

Use:

Ctrl + Z

to undo the material cleanup.

Compatibility

Tested with:

Cinema 4D 2023.1.2
Cinema 4D Standard materials

Other versions of Cinema 4D may also work, but have not been tested.

Limitations

The script currently focuses on Cinema 4D Standard materials.

Non-Standard materials are ignored.

Examples may include:

Redshift materials
V-Ray materials
Corona materials
Third-party renderer materials

Texture comparison currently uses the texture path.

Two identical image files stored in different locations may therefore be considered different materials.

Example:

C:\Project_A\Textures\beton.jpg

and:

D:\Archive\Textures\beton.jpg

will currently be treated as different texture paths even if the image files are identical.

Warning

Although the script is designed to be conservative, always save your Cinema 4D scene before running cleanup operations.

For important production files, testing on a copy of the scene is recommended.

Typical use cases

Useful for:

Archicad imports
BIM imports
Merged Cinema 4D scenes
Large architectural visualization projects
CAD conversion workflows
Cleaning duplicated materials after copy/paste operations
Preparing heavy scenes for rendering or real-time visualization
License

MIT



