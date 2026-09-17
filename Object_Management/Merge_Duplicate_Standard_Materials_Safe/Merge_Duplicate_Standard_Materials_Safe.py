import c4d
import os
import re


"""
Merge Duplicate Standard Materials - SAFE V4

Tested with:
Cinema 4D 2023.1.2

PURPOSE
-------
Find duplicated Cinema 4D Standard materials and merge them
ONLY when their actual content is identical.

Material names are normalized before comparison.

Examples considered as belonging to the same family:

BETON
BETON.1
BETON.2
BETON (1)
BETON(2)
BETON.1 (2)

Extra spaces are also normalized.

IMPORTANT
---------
Same name does NOT automatically mean merge.

Materials are merged only when:
- channel activation states are identical
- material parameters are identical
- shaders are identical
- textures are identical
- texture paths are identical
- shader parameters are identical

If any detected difference exists, both materials are preserved.
"""


# ============================================================
# MATERIAL NAME NORMALIZATION
# ============================================================

def get_base_material_name(name):
    """
    Normalise les noms de matériaux.

    Exemples :

    BETON                    -> BETON
    BETON.1                  -> BETON
    BETON.025                -> BETON
    BETON (1)                -> BETON
    BETON(2)                 -> BETON
    BETON.1 (2)              -> BETON

    Les espaces multiples sont également réduits.

    Exemple :

    Isolation  -  Panneau rigide bleu
    ->
    Isolation - Panneau rigide bleu
    """

    if not name:
        return ""

    # Supprime espaces début / fin
    name = name.strip()

    # Plusieurs espaces -> un seul
    name = re.sub(
        r"\s+",
        " ",
        name
    )

    # --------------------------------------------------------
    # Retire les suffixes plusieurs fois.
    #
    # Exemple :
    #
    # BETON.1 (2)
    # -> BETON.1
    # -> BETON
    # --------------------------------------------------------

    while True:

        old_name = name

        # Suffixes :
        # (1)
        #  (2)
        #   (15)
        name = re.sub(
            r"\s*\(\d+\)\s*$",
            "",
            name
        )

        name = name.strip()

        # Suffixes :
        # .1
        # .2
        # .015
        name = re.sub(
            r"\.\d+\s*$",
            "",
            name
        )

        name = name.strip()

        # Re-nettoyage des espaces
        name = re.sub(
            r"\s+",
            " ",
            name
        )

        if name == old_name:
            break

    return name.strip()


# ============================================================
# SAFE PARAMETER ACCESS
# ============================================================

def safe_get(node, parameter_id):
    """
    Lit un paramètre C4D sans provoquer d'erreur
    si le paramètre n'existe pas dans cette version.
    """

    if parameter_id is None:
        return None

    try:
        return node[parameter_id]

    except Exception:

        try:

            desc_id = c4d.DescID(
                c4d.DescLevel(parameter_id)
            )

            return node.GetParameter(
                desc_id,
                c4d.DESCFLAGS_GET_0
            )

        except Exception:

            return None


# ============================================================
# TEXTURE PATH NORMALIZATION
# ============================================================

def normalize_filename(value):
    """
    Normalise les chemins de texture.
    """

    try:
        path = value.GetString()

    except Exception:

        try:
            path = str(value)

        except Exception:
            return ""

    if not path:
        return ""

    try:

        path = os.path.normpath(
            path
        )

        path = os.path.normcase(
            path
        )

    except Exception:
        pass

    return path


# ============================================================
# GENERIC VALUE FINGERPRINT
# ============================================================

def fingerprint_value(value):
    """
    Transforme une valeur Cinema 4D en valeur comparable.
    """

    if value is None:
        return ("NONE",)

    # --------------------------------------------------------
    # Bool
    # --------------------------------------------------------

    if isinstance(value, bool):

        return (
            "BOOL",
            value
        )

    # --------------------------------------------------------
    # Integer
    # --------------------------------------------------------

    if isinstance(value, int):

        return (
            "INT",
            value
        )

    # --------------------------------------------------------
    # Float
    # --------------------------------------------------------

    if isinstance(value, float):

        return (
            "FLOAT",
            round(value, 8)
        )

    # --------------------------------------------------------
    # String
    # --------------------------------------------------------

    if isinstance(value, str):

        return (
            "STRING",
            value
        )

    # --------------------------------------------------------
    # Vector
    # --------------------------------------------------------

    if isinstance(value, c4d.Vector):

        return (
            "VECTOR",
            round(value.x, 8),
            round(value.y, 8),
            round(value.z, 8)
        )

    # --------------------------------------------------------
    # Matrix
    # --------------------------------------------------------

    if isinstance(value, c4d.Matrix):

        return (
            "MATRIX",

            fingerprint_value(
                value.off
            ),

            fingerprint_value(
                value.v1
            ),

            fingerprint_value(
                value.v2
            ),

            fingerprint_value(
                value.v3
            )
        )

    # --------------------------------------------------------
    # Filename
    # --------------------------------------------------------

    if isinstance(value, c4d.Filename):

        return (
            "FILENAME",
            normalize_filename(value)
        )

    # --------------------------------------------------------
    # BaseContainer
    # --------------------------------------------------------

    if isinstance(value, c4d.BaseContainer):

        return (
            "CONTAINER",
            fingerprint_container(value)
        )

    # --------------------------------------------------------
    # Cinema 4D links
    #
    # Ne pas stocker directement l'objet car certains objets
    # Cinema 4D ne sont pas hashables.
    # --------------------------------------------------------

    if isinstance(value, c4d.BaseList2D):

        try:
            object_type = value.GetType()
        except Exception:
            object_type = 0

        return (
            "C4D_LINK",
            object_type
        )

    # --------------------------------------------------------
    # Autres types
    #
    # Comportement volontairement conservateur :
    # une valeur inconnue doit avoir exactement la même
    # représentation pour permettre une fusion.
    # --------------------------------------------------------

    try:

        return (
            "OTHER",
            type(value).__name__,
            repr(value)
        )

    except Exception:

        return (
            "UNKNOWN",
            type(value).__name__
        )


# ============================================================
# BASE CONTAINER FINGERPRINT
# Compatible Cinema 4D 2023.1.2
# ============================================================

def fingerprint_container(container):
    """
    Analyse les paramètres contenus dans un BaseContainer.
    """

    result = []

    try:
        count = len(container)

    except Exception:
        return tuple()

    for i in range(count):

        # ----------------------------------------------------
        # ID du paramètre
        # ----------------------------------------------------

        try:
            parameter_id = container.GetIndexId(i)

        except Exception:
            continue

        if parameter_id == c4d.NOTOK:
            continue

        # ----------------------------------------------------
        # Valeur
        # ----------------------------------------------------

        try:

            value = container.GetIndexData(i)

        except Exception:

            try:

                value = container.GetData(
                    parameter_id
                )

            except Exception:

                continue

        # ----------------------------------------------------
        # Empreinte
        # ----------------------------------------------------

        result.append(
            (
                parameter_id,
                fingerprint_value(value)
            )
        )

    # --------------------------------------------------------
    # Stabilise l'ordre pour éviter les faux différents
    # --------------------------------------------------------

    try:

        result.sort(
            key=lambda item: item[0]
        )

    except Exception:
        pass

    return tuple(result)


# ============================================================
# SHADER FINGERPRINT
# ============================================================

def fingerprint_shader(shader):
    """
    Analyse un shader et tous ses sous-shaders.
    """

    if shader is None:

        return (
            "NO_SHADER",
        )

    # --------------------------------------------------------
    # Type du shader
    # --------------------------------------------------------

    try:
        shader_type = shader.GetType()

    except Exception:
        shader_type = 0

    # --------------------------------------------------------
    # Paramètres
    # --------------------------------------------------------

    try:

        shader_parameters = fingerprint_container(
            shader.GetData()
        )

    except Exception:

        shader_parameters = ()

    # --------------------------------------------------------
    # Sous-shaders
    # --------------------------------------------------------

    children = []

    try:
        child = shader.GetDown()

    except Exception:
        child = None

    while child:

        children.append(
            fingerprint_shader(child)
        )

        child = child.GetNext()

    return (
        "SHADER",
        shader_type,
        shader_parameters,
        tuple(children)
    )


# ============================================================
# COMPLETE SHADER TREE
# ============================================================

def fingerprint_complete_shader_tree(material):
    """
    Analyse tous les shaders présents dans le matériau.
    """

    result = []

    try:
        shader = material.GetFirstShader()

    except Exception:
        shader = None

    while shader:

        result.append(
            fingerprint_shader(shader)
        )

        shader = shader.GetNext()

    return tuple(result)


# ============================================================
# STANDARD MATERIAL CHANNEL DEFINITIONS
# ============================================================

def get_channel_definitions():
    """
    Liste les principaux canaux des matériaux Standard C4D.

    getattr permet de rester compatible si une constante
    n'existe pas dans certaines versions.
    """

    possible_channels = [

        (
            "COLOR",
            "MATERIAL_USE_COLOR",
            "MATERIAL_COLOR_SHADER"
        ),

        (
            "DIFFUSION",
            "MATERIAL_USE_DIFFUSION",
            "MATERIAL_DIFFUSION_SHADER"
        ),

        (
            "LUMINANCE",
            "MATERIAL_USE_LUMINANCE",
            "MATERIAL_LUMINANCE_SHADER"
        ),

        (
            "TRANSPARENCY",
            "MATERIAL_USE_TRANSPARENCY",
            "MATERIAL_TRANSPARENCY_SHADER"
        ),

        (
            "REFLECTION",
            "MATERIAL_USE_REFLECTION",
            "MATERIAL_REFLECTION_SHADER"
        ),

        (
            "ENVIRONMENT",
            "MATERIAL_USE_ENVIRONMENT",
            "MATERIAL_ENVIRONMENT_SHADER"
        ),

        (
            "FOG",
            "MATERIAL_USE_FOG",
            None
        ),

        (
            "BUMP",
            "MATERIAL_USE_BUMP",
            "MATERIAL_BUMP_SHADER"
        ),

        (
            "NORMAL",
            "MATERIAL_USE_NORMAL",
            "MATERIAL_NORMAL_SHADER"
        ),

        (
            "ALPHA",
            "MATERIAL_USE_ALPHA",
            "MATERIAL_ALPHA_SHADER"
        ),

        (
            "GLOW",
            "MATERIAL_USE_GLOW",
            None
        ),

        (
            "DISPLACEMENT",
            "MATERIAL_USE_DISPLACEMENT",
            "MATERIAL_DISPLACEMENT_SHADER"
        )
    ]

    definitions = []

    for channel_name, use_name, shader_name in possible_channels:

        # ----------------------------------------------------
        # Activation du canal
        # ----------------------------------------------------

        use_id = getattr(
            c4d,
            use_name,
            None
        )

        if use_id is None:
            continue

        # ----------------------------------------------------
        # Shader associé
        # ----------------------------------------------------

        shader_id = None

        if shader_name is not None:

            shader_id = getattr(
                c4d,
                shader_name,
                None
            )

        definitions.append(
            (
                channel_name,
                use_id,
                shader_id
            )
        )

    return definitions


# ============================================================
# CHANNEL FINGERPRINT
# ============================================================

def fingerprint_channels(material):
    """
    Compare explicitement :

    - canal actif / inactif
    - présence d'un shader
    - contenu du shader
    """

    result = []

    channels = get_channel_definitions()

    for channel_name, use_id, shader_id in channels:

        # ----------------------------------------------------
        # Canal actif ?
        # ----------------------------------------------------

        enabled_value = safe_get(
            material,
            use_id
        )

        enabled = bool(
            enabled_value
        )

        # ----------------------------------------------------
        # Shader
        # ----------------------------------------------------

        shader_signature = (
            "NO_SHADER",
        )

        if shader_id is not None:

            shader = safe_get(
                material,
                shader_id
            )

            shader_signature = fingerprint_shader(
                shader
            )

        # ----------------------------------------------------
        # Résultat
        # ----------------------------------------------------

        result.append(
            (
                channel_name,
                enabled,
                shader_signature
            )
        )

    return tuple(result)


# ============================================================
# COMPLETE MATERIAL FINGERPRINT
# ============================================================

def material_fingerprint(material):
    """
    Crée une empreinte complète du matériau.

    La comparaison comprend :

    - paramètres généraux
    - valeurs des canaux
    - activation des canaux
    - shaders
    - textures
    - sous-shaders
    """

    # --------------------------------------------------------
    # Paramètres généraux du matériau
    # --------------------------------------------------------

    try:

        material_data = fingerprint_container(
            material.GetData()
        )

    except Exception:

        material_data = ()

    # --------------------------------------------------------
    # Canaux
    # --------------------------------------------------------

    try:

        channel_data = fingerprint_channels(
            material
        )

    except Exception:

        channel_data = ()

    # --------------------------------------------------------
    # Tous les shaders du matériau
    # --------------------------------------------------------

    try:

        complete_shader_tree = fingerprint_complete_shader_tree(
            material
        )

    except Exception:

        complete_shader_tree = ()

    return (
        material.GetType(),
        channel_data,
        material_data,
        complete_shader_tree
    )


# ============================================================
# REPLACEMENT LOOKUP
# ============================================================

def find_replacement(material, replacements):
    """
    replacements :

    [
        (doublon, matériau_conservé),
        ...
    ]
    """

    for duplicate, keeper in replacements:

        try:

            if material == duplicate:
                return keeper

        except Exception:
            pass

    return None


# ============================================================
# REPLACE MATERIALS ON TEXTURE TAGS
# ============================================================

def replace_material_tags(doc, replacements):
    """
    Remplace les doublons sur tous les Texture Tags
    de la scène.
    """

    def walk(obj):

        while obj:

            # ------------------------------------------------
            # Tags
            # ------------------------------------------------

            tag = obj.GetFirstTag()

            while tag:

                next_tag = tag.GetNext()

                if tag.CheckType(c4d.Ttexture):

                    old_material = tag.GetMaterial()

                    if old_material is not None:

                        new_material = find_replacement(
                            old_material,
                            replacements
                        )

                        if new_material is not None:

                            doc.AddUndo(
                                c4d.UNDOTYPE_CHANGE,
                                tag
                            )

                            tag.SetMaterial(
                                new_material
                            )

                tag = next_tag

            # ------------------------------------------------
            # Enfants
            # ------------------------------------------------

            walk(
                obj.GetDown()
            )

            # ------------------------------------------------
            # Objet suivant
            # ------------------------------------------------

            obj = obj.GetNext()

    walk(
        doc.GetFirstObject()
    )


# ============================================================
# MAIN
# ============================================================

def main():

    doc = c4d.documents.GetActiveDocument()

    materials = doc.GetMaterials()

    if not materials:

        c4d.gui.MessageDialog(
            "Aucun matériau trouvé."
        )

        return

    # ========================================================
    # KEEP ONLY STANDARD MATERIALS
    # ========================================================

    standard_materials = []

    ignored_materials = 0

    for material in materials:

        if material.GetType() == c4d.Mmaterial:

            standard_materials.append(
                material
            )

        else:

            ignored_materials += 1

    if not standard_materials:

        c4d.gui.MessageDialog(
            "Aucun matériau Standard trouvé."
        )

        return

    # ========================================================
    # GROUP MATERIALS BY NORMALIZED NAME
    # ========================================================

    families = {}

    for material in standard_materials:

        base_name = get_base_material_name(
            material.GetName()
        )

        if base_name not in families:

            families[
                base_name
            ] = []

        families[
            base_name
        ].append(
            material
        )

    # ========================================================
    # SEARCH FOR TRUE DUPLICATES
    # ========================================================

    replacements = []

    duplicate_name_count = 0

    different_variant_count = 0

    # --------------------------------------------------------
    # Chaque famille
    # --------------------------------------------------------

    for base_name, family in families.items():

        if len(family) < 2:
            continue

        duplicate_name_count += (
            len(family) - 1
        )

        # ----------------------------------------------------
        # Le nom propre original est prioritaire.
        #
        # BETON
        # avant
        # BETON.1
        # BETON (1)
        # ----------------------------------------------------

        family.sort(
            key=lambda mat:
            (
                0
                if mat.GetName().strip() == base_name
                else 1
            )
        )

        # ----------------------------------------------------
        # Empreintes distinctes
        # ----------------------------------------------------

        fingerprint_groups = {}

        for material in family:

            fingerprint = material_fingerprint(
                material
            )

            # ------------------------------------------------
            # Première occurrence :
            # on la conserve.
            # ------------------------------------------------

            if fingerprint not in fingerprint_groups:

                fingerprint_groups[
                    fingerprint
                ] = material

            # ------------------------------------------------
            # Même empreinte :
            # véritable doublon.
            # ------------------------------------------------

            else:

                keeper = fingerprint_groups[
                    fingerprint
                ]

                replacements.append(
                    (
                        material,
                        keeper
                    )
                )

        # ----------------------------------------------------
        # Compte les variantes réellement différentes
        # ----------------------------------------------------

        if len(fingerprint_groups) > 1:

            different_variant_count += (
                len(fingerprint_groups) - 1
            )

    # ========================================================
    # NOTHING TO MERGE
    # ========================================================

    if not replacements:

        c4d.gui.MessageDialog(
            "Analyse terminée.\n\n"
            "Aucun matériau strictement identique "
            "à fusionner.\n\n"
            "{} doublon(s) de nom détecté(s).\n"
            "{} variante(s) différente(s) conservée(s).\n"
            "{} matériau(x) non-Standard ignoré(s).".format(
                duplicate_name_count,
                different_variant_count,
                ignored_materials
            )
        )

        return

    # ========================================================
    # CONFIRMATION BEFORE MODIFYING THE SCENE
    # ========================================================

    confirmation = c4d.gui.QuestionDialog(
        "{} matériau(x) strictement identique(s) "
        "ont été détecté(s).\n\n"
        "{} variante(s) de même nom seront conservée(s) "
        "car différentes.\n\n"
        "Fusionner les doublons maintenant ?".format(
            len(replacements),
            different_variant_count
        )
    )

    if not confirmation:
        return

    # ========================================================
    # UNDO
    # ========================================================

    doc.StartUndo()

    try:

        # ----------------------------------------------------
        # Replace materials on objects
        # ----------------------------------------------------

        replace_material_tags(
            doc,
            replacements
        )

        # ----------------------------------------------------
        # Delete duplicated materials
        # ----------------------------------------------------

        for duplicate, keeper in replacements:

            doc.AddUndo(
                c4d.UNDOTYPE_DELETEOBJ,
                duplicate
            )

            duplicate.Remove()

    finally:

        doc.EndUndo()

    # ========================================================
    # UPDATE CINEMA 4D
    # ========================================================

    c4d.EventAdd()

    # ========================================================
    # FINAL REPORT
    # ========================================================

    c4d.gui.MessageDialog(
        "Nettoyage terminé.\n\n"
        "{} matériau(x) identique(s) fusionné(s).\n"
        "{} variante(s) de même nom conservée(s) "
        "car différentes.\n"
        "{} matériau(x) non-Standard ignoré(s).\n\n"
        "Ctrl + Z permet d'annuler l'opération.".format(
            len(replacements),
            different_variant_count,
            ignored_materials
        )
    )


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":
    main()