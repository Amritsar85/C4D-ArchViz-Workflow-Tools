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

def get_children_recursive(op):
    """Récupère tous les enfants récursivement."""
    children = []
    for child in op.GetChildren():
        children.append(child)
        children.extend(get_children_recursive(child))
    return children

def deselect_all(op):
    """Désélectionne tous les objets dans la hiérarchie."""
    while op:
        op.DelBit(c4d.BIT_ACTIVE)
        deselect_all(op.GetDown())
        op = op.GetNext()

def main():
    doc = c4d.documents.GetActiveDocument()
    selected_objects = doc.GetSelection()

    if not selected_objects:
        c4d.gui.MessageDialog("Veuillez sélectionner un ou plusieurs groupes parent.")
        return

    # Traitement de chaque groupe sélectionné
    for obj in selected_objects:
        # Assurez-vous qu'il s'agit d'un groupe parent (null object)
        if obj.GetType() != c4d.Onull:
            continue

        print(f"Traitement du groupe parent : {obj.GetName()}")

        # Récupère les enfants du groupe parent sélectionné
        children = get_children_recursive(obj)

        if not children:
            continue  # S'il n'y a pas d'enfants, on passe au groupe suivant

        # Désélectionner tous les objets
        deselect_all(doc.GetFirstObject())

        # Sélectionner tous les enfants du groupe parent
        for child in children:
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, child)
            child.SetBit(c4d.BIT_ACTIVE)

        c4d.EventAdd()

        # Vérifier que des objets sont sélectionnés avant d'exécuter la commande
        if not doc.GetSelection():
            c4d.gui.MessageDialog("Aucun objet sélectionné pour la commande Connect Objects + Delete.")
            continue

        # Appliquer la commande Connect Objects + Delete à chaque groupe et ses enfants
        print(f"Appel de la commande Connect Objects + Delete pour le groupe : {obj.GetName()}")
        c4d.CallCommand(16768)  # Connect Objects + Delete

        c4d.EventAdd()

if __name__ == '__main__':
    main()
