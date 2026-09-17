import c4d

def main():
    doc = c4d.documents.GetActiveDocument()
    objects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_NONE)

    if not objects:
        c4d.gui.MessageDialog("Aucun objet sélectionné")
        return

    # Popup pour entrer le nom
    base_name = c4d.gui.InputDialog("Nouveau nom des objets :", "")
    if not base_name:
        return

    doc.StartUndo()

    # Numérotation incrémentale à partir de 0001
    for i, obj in enumerate(objects, start=1):
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
        number = str(i).zfill(4)  # 0001, 0002, 0003...
        obj.SetName(f"{base_name}_{number}")

    doc.EndUndo()
    c4d.EventAdd()

main()
