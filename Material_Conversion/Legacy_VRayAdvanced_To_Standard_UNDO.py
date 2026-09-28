import c4d
import os
import re

# ---------- Helpers ----------

ROLE_RULES = [
    (r"(opacity|transparenc|alpha|opac)", "alpha"),
    (r"(emissive|emit|self[_-]?illum|glow|lumin)", "emit"),
    (r"(normal|nrm|_n\.)", "normal"),
    (r"(bump|height|disp)", "bump"),
    (r"(rough|gloss)", "rough"),
    (r"(spec|specular)", "spec"),
    (r"(metal|metallic)", "metal"),
    (r"(diffuse|albedo|basecolor|col)", "diffuse"),
]


def classify_path(path):
    if not path:
        return None

    name = os.path.basename(str(path)).lower()

    for pattern, role in ROLE_RULES:
        if re.search(pattern, name):
            return role

    return None


def iter_tree(node):
    """Iterates recursively through a Cinema 4D hierarchy/tree."""
    while node:
        yield node

        child = node.GetDown()
        if child:
            for sub in iter_tree(child):
                yield sub

        node = node.GetNext()


def shader_paths_generic(shader):
    """
    Returns {role: [(shader, descid, filename)]} by inspecting all properties
    of a single shader node.
    """
    roles = {}

    if shader is None:
        return roles

    # Standard Bitmap shader
    if shader.CheckType(c4d.Xbitmap):
        filename = shader[c4d.BITMAPSHADER_FILENAME]
        role = classify_path(filename)

        if role:
            roles.setdefault(role, []).append(
                (shader, None, filename)
            )

        return roles

    # Generic shader inspection
    try:
        desc = c4d.Description()
        ok = shader.GetDescription(
            desc,
            c4d.DESCFLAGS_DESC_0
        )
    except Exception:
        ok = False

    if not ok:
        return roles

    handle = desc.GetFirst()

    while handle:
        try:
            desc_id = handle[0]
            value = shader.GetParameter(
                desc_id,
                c4d.DESCFLAGS_GET_0
            )
        except Exception:
            value = None

        if isinstance(value, c4d.Filename):
            path = value.GetString()

            if path:
                role = classify_path(path)

                if role:
                    roles.setdefault(role, []).append(
                        (shader, desc_id, path)
                    )

        handle = desc.GetNext(handle)

    return roles


def collect_roles_from_material(mat):
    """
    Scans each shader in the material exactly once and groups detected textures
    by semantic role.
    """
    collected = {}

    root_shader = mat.GetFirstShader()

    for shader in iter_tree(root_shader):
        sub = shader_paths_generic(shader)

        for role, items in sub.items():
            if role not in collected:
                collected[role] = items[:]

    return collected


def clone_or_make_bitmap(dst_mat, src_shader, descid, filename):
    """
    Clones a standard Bitmap shader when possible.
    Otherwise creates a Cinema 4D Bitmap shader pointing to the same file.
    """
    if src_shader and src_shader.CheckType(c4d.Xbitmap):
        clone = src_shader.GetClone()

        if clone:
            dst_mat.InsertShader(clone)
            clone.Message(c4d.MSG_UPDATE)
            return clone

    bmp = c4d.BaseShader(c4d.Xbitmap)

    if bmp:
        bmp[c4d.BITMAPSHADER_FILENAME] = filename
        dst_mat.InsertShader(bmp)
        bmp.Message(c4d.MSG_UPDATE)
        return bmp

    return None


def ensure_reflectance_layer(mat, roughness=0.25):
    try:
        mat[c4d.MATERIAL_USE_REFLECTION] = True

        bc = mat.GetDataInstance()
        layers = bc.GetContainerInstance(
            c4d.MATERIAL_REFLECTANCE_CONTAINER
        )

        if layers is None or layers.GetContainerCount() == 0:
            layer = c4d.BaseContainer()
            layer[c4d.REFLECTANCE_LAYER_ACTIVE] = True
            layer[c4d.REFLECTANCE_LAYER_NAME] = "Converted GGX"
            layer[c4d.REFLECTANCE_LAYER_MAIN_DISTRIBUTION] = (
                c4d.REFLECTANCE_DISTRIBUTION_GGX
            )
            layer[c4d.REFLECTANCE_LAYER_MAIN_VALUE_ROUGHNESS] = float(
                roughness
            )
            layer[c4d.REFLECTANCE_LAYER_FRESNEL_MODE] = (
                c4d.REFLECTANCE_FRESNEL_DIELECTRIC
            )
            layer[c4d.REFLECTANCE_LAYER_FRESNEL_IOR] = 1.5

            layers = c4d.BaseContainer()
            layers.InsertContainer(0, layer)

            bc.SetContainer(
                c4d.MATERIAL_REFLECTANCE_CONTAINER,
                layers
            )

    except Exception:
        pass


def replace_material_on_tags(doc, old_mat, new_mat):
    """
    Replaces old_mat with new_mat on all Texture Tags in the document.
    Each modified tag is registered in Cinema 4D's Undo system.
    """
    def walk(obj):
        while obj:
            tag = obj.GetFirstTag()

            while tag:
                next_tag = tag.GetNext()

                if (
                    tag.CheckType(c4d.Ttexture)
                    and tag.GetMaterial() == old_mat
                ):
                    doc.AddUndo(
                        c4d.UNDOTYPE_CHANGE,
                        tag
                    )
                    tag.SetMaterial(new_mat)

                tag = next_tag

            child = obj.GetDown()

            if child:
                walk(child)

            obj = obj.GetNext()

    walk(doc.GetFirstObject())


def is_vray_advanced(mat):
    type_name = (mat.GetTypeName() or "").lower()

    return (
        "vrayadvancedmaterial" in type_name
        or "v-ray advanced material" in type_name
    )


# ---------- Conversion ----------

def convert(doc):
    converted = 0
    scanned = 0

    vray_materials = [
        mat
        for mat in doc.GetMaterials()
        if is_vray_advanced(mat)
    ]

    scanned = len(vray_materials)

    if scanned == 0:
        c4d.gui.MessageDialog(
            "Aucun 'VRayAdvancedMaterial' trouvé."
        )
        return

    doc.StartUndo()

    try:
        for src in vray_materials:
            role_map = collect_roles_from_material(src)

            dst = c4d.BaseMaterial(c4d.Mmaterial)

            if dst is None:
                continue

            dst.SetName(
                "{}_STD".format(src.GetName())
            )

            # Diffuse / Color
            dst[c4d.MATERIAL_USE_COLOR] = True

            if "diffuse" in role_map:
                src_shader, desc_id, filename = role_map["diffuse"][0]
                bmp = clone_or_make_bitmap(
                    dst,
                    src_shader,
                    desc_id,
                    filename
                )

                if bmp:
                    dst[c4d.MATERIAL_COLOR_SHADER] = bmp

            # Alpha
            if "alpha" in role_map:
                dst[c4d.MATERIAL_USE_ALPHA] = True

                src_shader, desc_id, filename = role_map["alpha"][0]
                bmp = clone_or_make_bitmap(
                    dst,
                    src_shader,
                    desc_id,
                    filename
                )

                if bmp:
                    dst[c4d.MATERIAL_ALPHA_SHADER] = bmp

            # Emission / Luminance
            if "emit" in role_map:
                dst[c4d.MATERIAL_USE_LUMINANCE] = True

                src_shader, desc_id, filename = role_map["emit"][0]
                bmp = clone_or_make_bitmap(
                    dst,
                    src_shader,
                    desc_id,
                    filename
                )

                if bmp:
                    dst[c4d.MATERIAL_LUMINANCE_SHADER] = bmp

            # Bump / Normal
            bump_src = (
                role_map.get("bump")
                or role_map.get("normal")
            )

            if bump_src:
                src_shader, desc_id, filename = bump_src[0]

                dst[c4d.MATERIAL_USE_BUMP] = True

                bmp = clone_or_make_bitmap(
                    dst,
                    src_shader,
                    desc_id,
                    filename
                )

                if bmp:
                    dst[c4d.MATERIAL_BUMP_SHADER] = bmp
                    dst[c4d.MATERIAL_BUMP_STRENGTH] = 1.0

            ensure_reflectance_layer(
                dst,
                roughness=0.25
            )

            dst.Message(c4d.MSG_UPDATE)

            # Insert new material, then register it as a newly created object
            # in the Undo system.
            doc.InsertMaterial(dst)
            doc.AddUndo(
                c4d.UNDOTYPE_NEWOBJ,
                dst
            )

            replace_material_on_tags(
                doc,
                src,
                dst
            )

            converted += 1

    finally:
        doc.EndUndo()

    c4d.EventAdd()

    c4d.gui.MessageDialog(
        "Converti : {} / {} matériau(x) VRayAdvancedMaterial.\n\n"
        "Ctrl + Z permet d'annuler l'opération.".format(
            converted,
            scanned
        )
    )


def main():
    doc = c4d.documents.GetActiveDocument()
    convert(doc)


if __name__ == "__main__":
    main()
