"""
Connect Children And Delete

Purpose:
Optimizes heavy Cinema 4D hierarchies, particularly imported Archicad scenes,
by recursively selecting all children of selected Null objects and running
Connect Objects + Delete.

Usage:
1. Select one or more parent Null objects.
2. Run the script.
3. The children of each selected group are connected.

WARNING:
The original child objects are deleted by Connect Objects + Delete.
Save your scene before processing large hierarchies.
"""

import c4d


CONNECT_OBJECTS_DELETE_CMD = 16768


def get_children_recursive(op):
    """Retourne tous les descendants d'un objet."""
    children = []

    for child in op.GetChildren():
        children.append(child)
        children.extend(get_children_recursive(child))

    return children


def deselect_all(op):
    """Désélectionne tous les objets de la scène."""
    while op:
        op.DelBit(c4d.BIT_ACTIVE)

        child = op.GetDown()
        if child:
            deselect_all(child)

        op = op.GetNext()


def main():
    doc = c4d.documents.GetActiveDocument()
    selected_objects = list(doc.GetSelection())

    if not selected_objects:
        c4d.gui.MessageDialog(
            "Veuillez sélectionner un ou plusieurs groupes parent."
        )
        return

    # Ne conserver que les Nulls sélectionnés.
    parent_groups = [
        obj for obj in selected_objects
        if obj.GetType() == c4d.Onull
    ]

    if not parent_groups:
        c4d.gui.MessageDialog(
            "Aucun groupe Null valide n'est sélectionné."
        )
        return

    doc.StartUndo()

    try:
        for obj in parent_groups:
            print("Traitement du groupe parent :", obj.GetName())

            children = get_children_recursive(obj)

            if not children:
                print("Aucun enfant trouvé :", obj.GetName())
                continue

            # Désélectionner toute la scène.
            deselect_all(doc.GetFirstObject())

            # Sélectionner tous les descendants du groupe courant.
            for child in children:
                doc.AddUndo(c4d.UNDOTYPE_BITS, child)
                child.SetBit(c4d.BIT_ACTIVE)

            c4d.EventAdd()

            if not doc.GetSelection():
                print(
                    "Aucun objet sélectionné pour Connect Objects + Delete :",
                    obj.GetName()
                )
                continue

            print(
                "Connect Objects + Delete :",
                obj.GetName()
            )

            # La commande native de Cinema 4D effectue la fusion
            # et la suppression des objets originaux.
            c4d.CallCommand(CONNECT_OBJECTS_DELETE_CMD)

    finally:
        doc.EndUndo()
        c4d.EventAdd()


if __name__ == "__main__":
    main()
