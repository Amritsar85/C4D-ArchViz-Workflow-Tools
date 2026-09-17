import c4d
import random
from c4d import gui


"""
Create Random Parcel Sweeps

Tested with:
Cinema 4D 2023.1.2

PURPOSE
-------
Creates one Sweep object for every selected spline.

A template Sweep must be selected LAST.

The template Sweep must contain a Rectangle as its first child.

The Rectangle height is randomized between values entered
by the user when the script starts.

USAGE
-----
1. Select the Null/group containing the parcel splines.
2. Hold Ctrl and select the template Sweep LAST.
3. Run the script.
4. Enter:
   - Minimum height
   - Maximum height
   - Random seed
5. Confirm.

FINAL HIERARCHY
---------------
Sweep_ParcelName
    Rectangle
    ParcelSpline
"""


# ============================================================
# DEFAULT VALUES
# ============================================================

DEFAULT_MIN_HEIGHT = 160.0
DEFAULT_MAX_HEIGHT = 220.0
DEFAULT_RANDOM_SEED = 12345


# ============================================================
# USER SETTINGS
# ============================================================

def get_user_settings():
    """
    Ask the user for:
    - Minimum height
    - Maximum height
    - Random seed

    Heights are entered in Cinema 4D units.
    In the current workflow:
    160 = 1.60 m
    220 = 2.20 m
    """

    # --------------------------------------------------------
    # Minimum height
    # --------------------------------------------------------

    value = gui.InputDialog(
        "Minimum Rectangle height\n"
        "Example: 160 = 1.60 m",
        str(DEFAULT_MIN_HEIGHT)
    )

    if value is None or value == "":
        return None

    try:
        min_height = float(
            value.replace(",", ".")
        )

    except ValueError:

        gui.MessageDialog(
            "Invalid minimum height."
        )

        return None

    # --------------------------------------------------------
    # Maximum height
    # --------------------------------------------------------

    value = gui.InputDialog(
        "Maximum Rectangle height\n"
        "Example: 220 = 2.20 m",
        str(DEFAULT_MAX_HEIGHT)
    )

    if value is None or value == "":
        return None

    try:
        max_height = float(
            value.replace(",", ".")
        )

    except ValueError:

        gui.MessageDialog(
            "Invalid maximum height."
        )

        return None

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if min_height < 0 or max_height < 0:

        gui.MessageDialog(
            "Height values must be positive."
        )

        return None

    if min_height > max_height:

        gui.MessageDialog(
            "Minimum height cannot be greater "
            "than maximum height."
        )

        return None

    # --------------------------------------------------------
    # Random seed
    # --------------------------------------------------------

    value = gui.InputDialog(
        "Random Seed\n"
        "Use the same number to reproduce "
        "the same random result.",
        str(DEFAULT_RANDOM_SEED)
    )

    if value is None or value == "":
        return None

    try:
        random_seed = int(value)

    except ValueError:

        gui.MessageDialog(
            "Random Seed must be an integer."
        )

        return None

    return (
        min_height,
        max_height,
        random_seed
    )


# ============================================================
# COLLECT SPLINES
# ============================================================

def collect_splines(obj, splines, template_sweep):
    """
    Recursively collects spline objects.

    Existing Sweep objects are ignored so that already
    processed geometry is not processed again.
    """

    # Do not process the template Sweep
    if obj == template_sweep:
        return

    # Ignore existing Sweep objects
    if obj.CheckType(c4d.Osweep):
        return

    # Spline found
    if obj.CheckType(c4d.Ospline):

        splines.append(
            obj
        )

        return

    # --------------------------------------------------------
    # Search children
    # --------------------------------------------------------

    child = obj.GetDown()

    while child:

        next_child = child.GetNext()

        collect_splines(
            child,
            splines,
            template_sweep
        )

        child = next_child


# ============================================================
# MAIN
# ============================================================

def main():

    # ========================================================
    # USER SETTINGS
    # ========================================================

    settings = get_user_settings()

    if settings is None:
        return

    min_height, max_height, random_seed = settings

    # Reproducible random distribution
    random.seed(
        random_seed
    )

    # ========================================================
    # SELECTION
    # ========================================================

    selected = doc.GetActiveObjects(
        c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER
    )

    if len(selected) < 2:

        gui.MessageDialog(
            "Select the parcel splines or their Null first,\n"
            "then select the template Sweep LAST."
        )

        return

    # --------------------------------------------------------
    # Last selected object = template Sweep
    # --------------------------------------------------------

    template_sweep = selected[-1]

    if not template_sweep.CheckType(c4d.Osweep):

        gui.MessageDialog(
            "The LAST selected object must be "
            "the template Sweep."
        )

        return

    # --------------------------------------------------------
    # Template Rectangle
    # --------------------------------------------------------

    template_rectangle = template_sweep.GetDown()

    if template_rectangle is None:

        gui.MessageDialog(
            "The template Sweep must contain "
            "a Rectangle as its first child."
        )

        return

    # Everything except the template Sweep
    roots = selected[:-1]

    # ========================================================
    # FIND SPLINES
    # ========================================================

    splines = []

    for root in roots:

        collect_splines(
            root,
            splines,
            template_sweep
        )

    if not splines:

        gui.MessageDialog(
            "No spline found in the selection."
        )

        return

    # ========================================================
    # CREATE SWEEPS
    # ========================================================

    doc.StartUndo()

    created = 0

    try:

        for spline in splines:

            # ------------------------------------------------
            # Keep spline global position
            # ------------------------------------------------

            spline_mg = spline.GetMg()

            # ------------------------------------------------
            # Clone template Sweep
            # ------------------------------------------------

            new_sweep = template_sweep.GetClone()

            if new_sweep is None:
                continue

            # ------------------------------------------------
            # Name
            # ------------------------------------------------

            new_sweep.SetName(
                "Sweep_" + spline.GetName()
            )

            # ------------------------------------------------
            # Insert Sweep before original spline
            # ------------------------------------------------

            new_sweep.InsertBefore(
                spline
            )

            # Reset local transformation
            new_sweep.SetMl(
                c4d.Matrix()
            )

            doc.AddUndo(
                c4d.UNDOTYPE_NEWOBJ,
                new_sweep
            )

            doc.AddUndo(
                c4d.UNDOTYPE_CHANGE,
                spline
            )

            # ------------------------------------------------
            # Rectangle
            # ------------------------------------------------

            rectangle = new_sweep.GetDown()

            if rectangle is not None:

                random_height = random.uniform(
                    min_height,
                    max_height
                )

                rectangle[
                    c4d.PRIM_RECTANGLE_HEIGHT
                ] = random_height

            # ------------------------------------------------
            # Final hierarchy:
            #
            # Sweep
            #     Rectangle
            #     Parcel spline
            # ------------------------------------------------

            spline.InsertUnderLast(
                new_sweep
            )

            # Restore original world position
            spline.SetMg(
                spline_mg
            )

            created += 1

    finally:

        doc.EndUndo()

    # ========================================================
    # UPDATE C4D
    # ========================================================

    c4d.EventAdd()

    # ========================================================
    # RESULT
    # ========================================================

    gui.MessageDialog(
        "{} Sweep(s) created.\n\n"
        "Minimum height: {}\n"
        "Maximum height: {}\n"
        "Random Seed: {}".format(
            created,
            min_height,
            max_height,
            random_seed
        )
    )


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":
    main()