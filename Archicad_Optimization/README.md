

# Connect Children And Delete

Cinema 4D Python utility for simplifying heavy object hierarchies, especially after importing models from Archicad.

## What it does

The script processes one or more selected parent **Null objects**.

For each selected Null, it:

1. Finds all child objects recursively.
2. Selects every object contained in the hierarchy.
3. Runs Cinema 4D's **Connect Objects + Delete** command.
4. Repeats the process for each selected parent Null.

This can be useful for large Archicad imports containing many nested objects and fragmented geometry.

## How to use

1. Import your Archicad model into Cinema 4D.
2. Select one or more parent **Null objects** containing the geometry you want to simplify.
3. Run `Connect_Children_And_Delete.py`.
4. The script selects all children recursively and executes **Connect Objects + Delete**.

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
