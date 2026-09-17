import c4d
from c4d import gui


# ============================================================
# RÉGLAGES
# ============================================================

# Le but est que toutes les parcelles soient orientées vers +Y
TARGET_UP_Y = True

# Petite tolérance pour éviter de traiter les formes dégénérées
EPSILON = 0.000001


# ============================================================
# RECHERCHE DES SPLINES
# ============================================================

def collect_splines(obj, splines):
    """
    Recherche récursivement toutes les splines.
    Ignore les générateurs déjà existants.
    """

    # Évite de modifier accidentellement des splines
    # déjà utilisées dans des générateurs
    if obj.CheckType(c4d.Osweep):
        return

    if obj.CheckType(c4d.Oloft):
        return

    if obj.CheckType(c4d.Oextrude):
        return

    # Spline trouvée
    if obj.CheckType(c4d.Ospline):
        splines.append(obj)
        return

    child = obj.GetDown()

    while child:
        next_child = child.GetNext()

        collect_splines(
            child,
            splines
        )

        child = next_child


# ============================================================
# SEGMENTS DE LA SPLINE
# ============================================================

def get_segments(spline):
    """
    Retourne :
    (index_debut, nombre_points, fermé)
    pour chaque segment de la spline.
    """

    result = []

    segment_count = spline.GetSegmentCount()

    # Cas simple : une spline sans segments multiples
    if segment_count == 0:

        result.append(
            (
                0,
                spline.GetPointCount(),
                spline.IsClosed()
            )
        )

        return result

    # Spline multi-segments
    offset = 0

    for i in range(segment_count):

        data = spline.GetSegment(i)

        count = data["cnt"]
        closed = data["closed"]

        result.append(
            (
                offset,
                count,
                closed
            )
        )

        offset += count

    return result


# ============================================================
# DIRECTION DE LA SPLINE
# ============================================================

def get_normal_y(points, mg, start, count):
    """
    Calcule le sens de la spline projetée sur XZ.

    Valeur positive  -> normale vers +Y
    Valeur négative  -> normale vers -Y

    Les vraies valeurs Y ne sont pas modifiées.
    """

    normal_y = 0.0

    for i in range(count):

        current_index = start + i
        next_index = start + ((i + 1) % count)

        # Passage en coordonnées globales
        p1 = mg * points[current_index]
        p2 = mg * points[next_index]

        # Composante Y du produit vectoriel
        # en projection XZ
        normal_y += (
            p1.z * p2.x
            -
            p1.x * p2.z
        )

    return normal_y


# ============================================================
# INVERSION D'UN SEGMENT
# ============================================================

def reverse_segment(points, tangents, start, count):
    """
    Inverse l'ordre des points d'un segment.

    Pour une spline Bézier, les tangentes gauche/droite
    sont également échangées.
    """

    old_points = points[start:start + count]

    reversed_points = list(
        reversed(old_points)
    )

    points[start:start + count] = reversed_points

    # --------------------------------------------------------
    # Tangentes Bézier
    # --------------------------------------------------------

    if tangents is not None:

        old_tangents = tangents[start:start + count]

        reversed_tangents = []

        for tangent in reversed(old_tangents):

            # En inversant le sens de la spline,
            # gauche et droite s'échangent.
            reversed_tangents.append(
                {
                    "vl": tangent["vr"],
                    "vr": tangent["vl"]
                }
            )

        tangents[start:start + count] = reversed_tangents


# ============================================================
# TRAITEMENT D'UNE SPLINE
# ============================================================

def process_spline(spline):
    """
    Vérifie tous les segments fermés d'une spline
    et retourne ceux qui pointent vers -Y.
    """

    points = spline.GetAllPoints()

    if len(points) < 3:
        return 0, 0

    mg = spline.GetMg()

    segments = get_segments(spline)

    # Vérifie si nous sommes sur une spline Bézier
    tangents = None

    try:

        if (
            spline.GetInterpolationType()
            == c4d.SPLINETYPE_BEZIER
        ):

            tangent_count = spline.GetTangentCount()

            if tangent_count == len(points):

                tangents = []

                for i in range(tangent_count):
                    tangents.append(
                        spline.GetTangent(i)
                    )

    except:
        tangents = None

    flipped = 0
    skipped = 0

    for start, count, closed in segments:

        # Une parcelle doit être fermée
        if not closed:
            skipped += 1
            continue

        if count < 3:
            skipped += 1
            continue

        normal_y = get_normal_y(
            points,
            mg,
            start,
            count
        )

        # Forme presque sans surface en projection XZ
        if abs(normal_y) < EPSILON:
            skipped += 1
            continue

        # ----------------------------------------------------
        # Si normale vers -Y -> inversion
        # ----------------------------------------------------

        if normal_y < 0.0:

            reverse_segment(
                points,
                tangents,
                start,
                count
            )

            flipped += 1

    # --------------------------------------------------------
    # Mise à jour de la spline
    # --------------------------------------------------------

    if flipped > 0:

        spline.SetAllPoints(points)

        # Restaurer les tangentes Bézier
        if tangents is not None:

            for i, tangent in enumerate(tangents):

                spline.SetTangent(
                    i,
                    tangent["vl"],
                    tangent["vr"]
                )

        spline.Message(
            c4d.MSG_UPDATE
        )

    return flipped, skipped


# ============================================================
# SCRIPT PRINCIPAL
# ============================================================

def main():

    selected = doc.GetActiveObjects(
        c4d.GETACTIVEOBJECTFLAGS_NONE
    )

    if not selected:

        gui.MessageDialog(
            "Sélectionne le groupe contenant "
            "tes parcelles DXF."
        )
        return

    # --------------------------------------------------------
    # Collecte des splines
    # --------------------------------------------------------

    splines = []

    for root in selected:

        collect_splines(
            root,
            splines
        )

    if not splines:

        gui.MessageDialog(
            "Aucune spline trouvée "
            "dans la sélection."
        )
        return

    # --------------------------------------------------------
    # Correction
    # --------------------------------------------------------

    doc.StartUndo()

    spline_count = 0
    flipped_splines = 0
    flipped_segments = 0
    skipped_segments = 0

    try:

        for spline in splines:

            spline_count += 1

            doc.AddUndo(
                c4d.UNDOTYPE_CHANGE,
                spline
            )

            flipped, skipped = process_spline(
                spline
            )

            if flipped > 0:
                flipped_splines += 1

            flipped_segments += flipped
            skipped_segments += skipped

    finally:

        doc.EndUndo()

    # Mise à jour Cinema 4D
    c4d.EventAdd()

    # --------------------------------------------------------
    # Résultat
    # --------------------------------------------------------

    message = (
        "Correction terminée.\n\n"
        "{} spline(s) analysée(s)\n"
        "{} spline(s) corrigée(s)\n"
        "{} segment(s) inversé(s)\n"
        "{} segment(s) ignoré(s)\n\n"
        "Les coordonnées X / Y / Z n'ont pas été modifiées."
    ).format(
        spline_count,
        flipped_splines,
        flipped_segments,
        skipped_segments
    )

    gui.MessageDialog(message)


# ============================================================
# EXÉCUTION
# ============================================================

if __name__ == "__main__":
    main()