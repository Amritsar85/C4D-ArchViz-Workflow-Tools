import c4d
import os, re

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
    for pat, role in ROLE_RULES:
        if re.search(pat, name):
            return role
    return None

def iter_tree(node):
    while node:
        yield node
        for child in iter_tree(node.GetDown()):
            yield child
        node = node.GetNext()

def shader_paths_generic(shader):
    """
    Retourne {role:[(shader, descid, filename)]} en inspectant TOUTES les propriétés
    des shaders (VRayBitmap inclus). Compatible API avec Description.GetFirst()/GetNext().
    """
    roles = {}
    if shader is None:
        return roles

    for sh in iter_tree(shader):
        # 1) Cas Bitmap standard
        if sh.CheckType(c4d.Xbitmap):
            fn = sh[c4d.BITMAPSHADER_FILENAME]
            role = classify_path(fn)
            if role:
                roles.setdefault(role, []).append((sh, None, fn))
            continue

        # 2) Cas générique : on inspecte la Description du shader
        try:
            desc = c4d.Description()
            ok = sh.GetDescription(desc, c4d.DESCFLAGS_DESC_0)
        except Exception:
            ok = False
        if not ok:
            continue

        h = desc.GetFirst()  # retourne un tuple (DescID, BaseContainer[, ...])
        while h:
            try:
                cid = h[0]  # c4d.DescID
                # Récupérer la valeur du paramètre via GetParameter (plus sûr que sh[cid])
                val = sh.GetParameter(cid, c4d.DESCFLAGS_GET_0)
            except Exception:
                val = None

            if isinstance(val, c4d.Filename):
                s = val.GetString()
                if s:
                    role = classify_path(s)
                    if role:
                        roles.setdefault(role, []).append((sh, cid, s))

            h = desc.GetNext(h)

    return roles

def collect_roles_from_material(mat):
    collected = {}
    sh = mat.GetFirstShader()
    for s in iter_tree(sh):
        sub = shader_paths_generic(s)
        for role, items in sub.items():
            if role not in collected:
                collected[role] = items[:]
    return collected

def clone_or_make_bitmap(dst_mat, src_shader, descid, filename):
    """Clone un shader bitmap si possible, sinon crée un Bitmap standard pointant sur filename."""
    if src_shader and src_shader.CheckType(c4d.Xbitmap):
        clone = src_shader.GetClone()
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
        layers = bc.GetContainerInstance(c4d.MATERIAL_REFLECTANCE_CONTAINER)
        if layers is None or layers.GetContainerCount() == 0:
            layer = c4d.BaseContainer()
            layer[c4d.REFLECTANCE_LAYER_ACTIVE] = True
            layer[c4d.REFLECTANCE_LAYER_NAME] = "Converted GGX"
            layer[c4d.REFLECTANCE_LAYER_MAIN_DISTRIBUTION] = c4d.REFLECTANCE_DISTRIBUTION_GGX
            layer[c4d.REFLECTANCE_LAYER_MAIN_VALUE_ROUGHNESS] = float(roughness)
            layer[c4d.REFLECTANCE_LAYER_FRESNEL_MODE] = c4d.REFLECTANCE_FRESNEL_DIELECTRIC
            layer[c4d.REFLECTANCE_LAYER_FRESNEL_IOR] = 1.5
            layers = c4d.BaseContainer()
            layers.InsertContainer(0, layer)
            bc.SetContainer(c4d.MATERIAL_REFLECTANCE_CONTAINER, layers)
    except Exception:
        pass

def replace_material_on_tags(doc, old_mat, new_mat):
    def walk(o):
        while o:
            t = o.GetFirstTag()
            while t:
                if t.CheckType(c4d.Ttexture) and t.GetMaterial() == old_mat:
                    t.SetMaterial(new_mat)
                t = t.GetNext()
            walk(o.GetDown())
            o = o.GetNext()
    walk(doc.GetFirstObject())

def is_vray_advanced(mat):
    tname = (mat.GetTypeName() or "").lower()
    return "vrayadvancedmaterial" in tname or "v-ray advanced material" in tname

# ---------- Conversion ----------
def convert(doc):
    converted, scanned = 0, 0
    for src in doc.GetMaterials():
        if not is_vray_advanced(src):
            continue
        scanned += 1

        role_map = collect_roles_from_material(src)  # {role:[(shader,descid,filename)]}

        dst = c4d.BaseMaterial(c4d.Mmaterial)
        dst.SetName(f"{src.GetName()}_STD")
        doc.InsertMaterial(dst)

        # Couleur / Diffuse
        dst[c4d.MATERIAL_USE_COLOR] = True
        if "diffuse" in role_map:
            sh, did, fn = role_map["diffuse"][0]
            bmp = clone_or_make_bitmap(dst, sh, did, fn)
            if bmp:
                dst[c4d.MATERIAL_COLOR_SHADER] = bmp

        # Alpha
        if "alpha" in role_map:
            dst[c4d.MATERIAL_USE_ALPHA] = True
            sh, did, fn = role_map["alpha"][0]
            bmp = clone_or_make_bitmap(dst, sh, did, fn)
            if bmp:
                dst[c4d.MATERIAL_ALPHA_SHADER] = bmp

        # Emissive
        if "emit" in role_map:
            dst[c4d.MATERIAL_USE_LUMINANCE] = True
            sh, did, fn = role_map["emit"][0]
            bmp = clone_or_make_bitmap(dst, sh, did, fn)
            if bmp:
                dst[c4d.MATERIAL_LUMINANCE_SHADER] = bmp

        # Bump / Normal (on met normal en bump si matériel Standard legacy)
        bump_src = role_map.get("bump") or role_map.get("normal")
        if bump_src:
            sh, did, fn = bump_src[0]
            dst[c4d.MATERIAL_USE_BUMP] = True
            bmp = clone_or_make_bitmap(dst, sh, did, fn)
            if bmp:
                dst[c4d.MATERIAL_BUMP_SHADER] = bmp
                dst[c4d.MATERIAL_BUMP_STRENGTH] = 1.0

        ensure_reflectance_layer(dst, roughness=0.25)
        dst.Message(c4d.MSG_UPDATE)
        replace_material_on_tags(doc, src, dst)
        converted += 1

    c4d.EventAdd()
    if scanned == 0:
        c4d.gui.MessageDialog("Aucun 'VRayAdvancedMaterial' trouvé.")
    else:
        c4d.gui.MessageDialog(f"Converti : {converted} / {scanned} matériau(x) VRayAdvancedMaterial.")

def main():
    doc = c4d.documents.GetActiveDocument()
    convert(doc)

if __name__ == "__main__":
    main()
