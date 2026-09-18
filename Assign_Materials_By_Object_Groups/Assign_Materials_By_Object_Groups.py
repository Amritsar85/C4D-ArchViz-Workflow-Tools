import c4d
import random
from c4d import gui


"""
Assign Materials By Object Groups

Tested with:
Cinema 4D 2023.1.2

PURPOSE
-------
Assign random Standard materials to selected objects
by groups of X objects.

Objects are processed in the exact Cinema 4D Object Manager
order, from TOP to BOTTOM.

USAGE
-----
- Select one or several objects
OR
- Select a Null/group containing the objects

Then run the script and enter the number of objects
that should share each material.

Null objects are used as containers and are not assigned
a material themselves.
"""


# ============================================================
# SETTINGS
# ============================================================

MATERIAL_PREFIX = "MAT_SCATTER_"
RANDOM_SEED = 12345
DEFAULT_GROUP_SIZE = 20


# ============================================================
# OBJECT COMPARISON
# ============================================================

def same_object(a, b):
    """
    Safe Cinema 4D object comparison.
    """

    if a is None or b is None:
        return False

    try:
        return a == b
    except Exception:
        return False


# ============================================================
# RANDOM COLOR
# ============================================================

def get_random_color():

    def rand():
        return random.uniform(
            0.3,
            1.0
        )

    return c4d.Vector(
        rand(),
        rand(),
        rand()
    )


# ============================================================
# CREATE MATERIAL
# ============================================================

def create_material(doc, index):

    mat = c4d.BaseMaterial(
        c4d.Mmaterial
    )

    if mat is None:
        return None

    mat.SetName(
        "{}{:03d}".format(
            MATERIAL_PREFIX,
            index
        )
    )

    mat[
        c4d.MATERIAL_USE_COLOR
    ] = True

    mat[
        c4d.MATERIAL_COLOR_COLOR
    ] = get_random_color()

    doc.InsertMaterial(
        mat
    )

    doc.AddUndo(
        c4d.UNDOTYPE_NEWOBJ,
        mat
    )

    return mat


# ============================================================
# UNIQUE OBJECT
# ============================================================

def append_unique(objects, obj):

    for existing in objects:

        if same_object(
            existing,
            obj
        ):
            return

    objects.append(
        obj
    )


# ============================================================
# OBJECT MANAGER ORDER
# ============================================================

def collect_scene_order(obj, result):
    """
    Collect complete scene hierarchy in the same visual order
    as the Cinema 4D Object Manager.
    """

    while obj:

        result.append(
            obj
        )

        child = obj.GetDown()

        if child is not None:

            collect_scene_order(
                child,
                result
            )

        obj = obj.GetNext()


# ============================================================
# CHECK SELECTION
# ============================================================

def object_is_selected(obj, selection):

    for selected in selection:

        if same_object(
            obj,
            selected
        ):
            return True

    return False


# ============================================================
# SELECTED PARENT
# ============================================================

def has_selected_parent(obj, selection):

    parent = obj.GetUp()

    while parent:

        if object_is_selected(
            parent,
            selection
        ):
            return True

        parent = parent.GetUp()

    return False


# ============================================================
# SORT SELECTION TOP TO BOTTOM
# ============================================================

def sort_selection_by_scene_order(
    doc,
    selection
):

    scene_order = []

    collect_scene_order(
        doc.GetFirstObject(),
        scene_order
    )

    ordered_selection = []

    for obj in scene_order:

        if object_is_selected(
            obj,
            selection
        ):

            ordered_selection.append(
                obj
            )

    return ordered_selection


# ============================================================
# COLLECT TARGET OBJECTS
# ============================================================

def collect_targets(obj, targets):
    """
    Null:
        Traverse its children.

    Other object:
        Add the object as one entity.

    Generator children such as the Rectangle/Spline inside
    a Sweep are therefore not counted separately.
    """

    if obj is None:
        return

    # --------------------------------------------------------
    # NULL = container
    # --------------------------------------------------------

    if obj.CheckType(
        c4d.Onull
    ):

        child = obj.GetDown()

        while child:

            next_child = child.GetNext()

            collect_targets(
                child,
                targets
            )

            child = next_child

        return

    # --------------------------------------------------------
    # REAL OBJECT
    # --------------------------------------------------------

    append_unique(
        targets,
        obj
    )


# ============================================================
# ASSIGN MATERIAL
# ============================================================

def assign_material(
    doc,
    obj,
    mat
):

    if obj is None:
        return False

    if mat is None:
        return False

    if obj.CheckType(
        c4d.Onull
    ):
        return False

    try:

        tag = obj.GetFirstTag()

        texture_tag = None

        # ----------------------------------------------------
        # FIND FIRST TEXTURE TAG
        # ----------------------------------------------------

        while tag:

            if tag.CheckType(
                c4d.Ttexture
            ):

                texture_tag = tag
                break

            tag = tag.GetNext()

        # ----------------------------------------------------
        # EXISTING TEXTURE TAG
        # ----------------------------------------------------

        if texture_tag is not None:

            doc.AddUndo(
                c4d.UNDOTYPE_CHANGE,
                texture_tag
            )

            texture_tag.SetMaterial(
                mat
            )

            return True

        # ----------------------------------------------------
        # CREATE TEXTURE TAG
        # ----------------------------------------------------

        texture_tag = c4d.TextureTag()

        if texture_tag is None:
            return False

        texture_tag.SetMaterial(
            mat
        )

        obj.InsertTag(
            texture_tag
        )

        doc.AddUndo(
            c4d.UNDOTYPE_NEWOBJ,
            texture_tag
        )

        return True

    except Exception:

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    doc = c4d.documents.GetActiveDocument()

    if doc is None:

        gui.MessageDialog(
            "Aucun document actif."
        )

        return

    random.seed(
        RANDOM_SEED
    )

    # ========================================================
    # NUMBER OF OBJECTS PER MATERIAL
    # ========================================================

    value = gui.InputDialog(
        "Nombre d'objets par matériau",
        str(DEFAULT_GROUP_SIZE)
    )

    if not value:
        return

    try:

        group_size = int(
            value
        )

        if group_size <= 0:
            raise ValueError

    except ValueError:

        gui.MessageDialog(
            "Entre un nombre entier supérieur à 0."
        )

        return

    # ========================================================
    # SELECTION
    # ========================================================

    selection = doc.GetActiveObjects(
        c4d.GETACTIVEOBJECTFLAGS_NONE
    )

    if not selection:

        gui.MessageDialog(
            "Sélectionne un ou plusieurs objets "
            "ou un groupe."
        )

        return

    # ========================================================
    # SORT SELECTION
    # ========================================================

    ordered_selection = (
        sort_selection_by_scene_order(
            doc,
            selection
        )
    )

    if not ordered_selection:

        gui.MessageDialog(
            "Impossible de retrouver la sélection "
            "dans la hiérarchie."
        )

        return

    # ========================================================
    # REMOVE CHILD SELECTIONS IF PARENT ALSO SELECTED
    # ========================================================

    roots = []

    for obj in ordered_selection:

        if not has_selected_parent(
            obj,
            ordered_selection
        ):

            roots.append(
                obj
            )

    # ========================================================
    # COLLECT TARGETS
    # ========================================================

    targets = []

    for root in roots:

        collect_targets(
            root,
            targets
        )

    if not targets:

        gui.MessageDialog(
            "Aucun objet à traiter trouvé."
        )

        return

    # ========================================================
    # UNDO
    # ========================================================

    doc.StartUndo()

    material_count = 0
    assigned_count = 0
    skipped_count = 0

    try:

        # ====================================================
        # GROUP OBJECTS TOP -> BOTTOM
        # ====================================================

        for start in range(
            0,
            len(targets),
            group_size
        ):

            material_count += 1

            mat = create_material(
                doc,
                material_count
            )

            if mat is None:
                continue

            group = targets[
                start:
                start + group_size
            ]

            for obj in group:

                if assign_material(
                    doc,
                    obj,
                    mat
                ):

                    assigned_count += 1

                else:

                    skipped_count += 1

    finally:

        doc.EndUndo()

    # ========================================================
    # REFRESH
    # ========================================================

    c4d.EventAdd()

    # ========================================================
    # RESULT
    # ========================================================

    gui.MessageDialog(
        "Traitement terminé.\n\n"
        "{} objet(s) trouvé(s).\n"
        "{} objet(s) assigné(s).\n"
        "{} objet(s) ignoré(s).\n\n"
        "{} objet(s) par matériau.\n"
        "{} matériau(x) créé(s).\n\n"
        "Ordre utilisé : haut vers bas.".format(
            len(targets),
            assigned_count,
            skipped_count,
            group_size,
            material_count
        )
    )


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":
    main()