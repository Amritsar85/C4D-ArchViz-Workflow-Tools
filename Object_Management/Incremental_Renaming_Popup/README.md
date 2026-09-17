# Incremental Renaming Popup

Simple Cinema 4D Python utility for quickly renaming multiple selected objects with an incremental number.

## What it does

The script renames all selected objects using a custom base name followed by a 4-digit incremental number.

Example:

```text
Cube
Cube.1
Cube.2
Cube.3

Enter:

Facade

Result:

Facade_0001
Facade_0002
Facade_0003
Facade_0004
How to use
Select the objects you want to rename in the Cinema 4D Object Manager.
Run:
Incremental_Renaming_Popup.py
A popup appears asking for the new base name.
Enter the desired name.
Confirm.

The selected objects will automatically be renamed using the following format:

NAME_0001
NAME_0002
NAME_0003
...
Example

If you select 5 objects and enter:

Window

The result will be:

Window_0001
Window_0002
Window_0003
Window_0004
Window_0005
Undo

The script supports Cinema 4D Undo.

You can use:

Ctrl + Z

to restore the previous object names.

Compatibility

Tested with:

Cinema 4D 2023.1.2

It may also work with other Cinema 4D versions, but they have not been tested.

Typical use cases

Useful for quickly organizing large Cinema 4D scenes, especially for:

Architecture
Archviz
Imported CAD / BIM models
Repetitive objects
Windows
Doors
Furniture
Vegetation
Scene cleanup
Notes

The numbering always starts at:

0001

and uses 4 digits.

License

MIT
