# Connect Children And Delete

Cinema 4D Python utility for simplifying heavy object hierarchies, especially after importing models from Archicad.

## What it does

The script processes one or more selected parent **Null objects**.

For each selected Null, it:

1. Finds all child objects recursively.
2. Selects every object contained in the hierarchy.
3. Runs Cinema 4D's **Connect Objects + Delete** command.
4. Repeats the process for each selected parent Null.
5. Keeps the operation compatible with Cinema 4D's **Undo** system.

This is especially useful for large Archicad imports containing many nested objects and fragmented geometry.

## How to use

1. Import your Archicad model into Cinema 4D.
2. Select one or more parent **Null objects** containing the geometry you want to simplify.
3. Run `Connect_Children_And_Delete.py`.
4. The script recursively selects all objects contained in each selected hierarchy.
5. Cinema 4D executes **Connect Objects + Delete** on the selected geometry.

## Undo

The script uses Cinema 4D's Undo system.

After processing several parent groups, you can use **Ctrl+Z** to progressively restore the previously processed groups.

## Example

Before:

```text
Building_Group
├── Wall_01
├── Wall_02
├── Windows
│   ├── Window_01
│   ├── Window_02
│   └── Window_03
├── Roof
└── Slab
```

After running the script, the hierarchy is simplified using Cinema 4D's **Connect Objects + Delete** command.

This can significantly reduce the number of objects in imported architectural scenes and make them easier to manage.

## Typical use cases

- Archicad imports
- Large architectural models
- Deeply nested object hierarchies
- Fragmented geometry
- Scene cleanup before rendering or export
- Preparing heavy scenes for tools such as D5 Render

## Warning

**Connect Objects + Delete is a destructive operation.**

The original child objects are replaced by connected geometry.

Although the script supports Undo, it is still recommended to save your Cinema 4D scene before processing large or important hierarchies.

## Requirements

- Cinema 4D
- Python scripting support
- Tested with standard Cinema 4D Null object hierarchies