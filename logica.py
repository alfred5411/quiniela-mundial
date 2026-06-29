def calcular_puntos_participante_json(participante, reales):

    # --- Validar JSON reales ---
    if not isinstance(reales, dict):
        raise ValueError("Reales no es un diccionario")

    for k in ["partidos", "clasificados", "fase_final", "premios"]:
        if k not in reales:
            raise KeyError(f"Falta clave '{k}' en resultados reales")

    partidos_p = participante["partidos"]
    clasificados_p = participante["clasificados"]
    fase_p = participante["fase_final"]
    premios_p = participante["premios"]

    # =========================
    # PARTIDOS
    # =========================

    pts_1x2 = pts_score = 0

    for p_p, p_r in zip(partidos_p, reales["partidos"]):

        if len(p_p) < 6 or len(p_r) < 6:
            continue

        m1p, m2p = p_p[3], p_p[4]
        m1r, m2r = p_r[3], p_r[4]

        if not m1p or not m2p or not m1r or not m2r:
            continue

        m1p, m2p = int(m1p), int(m2p)
        m1r, m2r = int(m1r), int(m2r)

        # 1-X-2
        res_p = (m1p > m2p) - (m1p < m2p)
        res_r = (m1r > m2r) - (m1r < m2r)

        if res_p == res_r:
            pts_1x2 += 4

        # Regla de 5+ goles
        m1p_cmp = min(m1p, 5)
        m2p_cmp = min(m2p, 5)
        m1r_cmp = min(m1r, 5)
        m2r_cmp = min(m2r, 5)

        if m1p_cmp == m1r_cmp and m2p_cmp == m2r_cmp:
            pts_score += 4
        elif m1p_cmp == m1r_cmp or m2p_cmp == m2r_cmp:
            pts_score += 1

    # =========================
    # GRUPOS
    # =========================

    pts_1ro = pts_2do = pts_3ro = pts_16vos = 0

    clasificados_16vos = []

    for lista in reales["clasificados"].values():
        clasificados_16vos.extend([e for e in lista if e])

    for grupo, posiciones in clasificados_p.items():

        if grupo not in reales["clasificados"]:
            continue

        reales_grupo = reales["clasificados"][grupo]

        p1 = posiciones[0] if len(posiciones) > 0 else ""
        p2 = posiciones[1] if len(posiciones) > 1 else ""
        p3 = posiciones[2] if len(posiciones) > 2 else ""

        if len(reales_grupo) > 0 and p1 == reales_grupo[0]:
            pts_1ro += 3

        if len(reales_grupo) > 1 and p2 == reales_grupo[1]:
            pts_2do += 4

        if len(reales_grupo) > 2 and p3 == reales_grupo[2]:
            pts_3ro += 5

        for equipo in [p1, p2, p3]:
            if equipo and equipo in clasificados_16vos:
                pts_16vos += 5

    # =========================
    # FASE FINAL
    # =========================

    pts_8vos = pts_4tos = pts_sf = pts_f = 0

    fase_real = reales["fase_final"]

    for equipo in fase_p.get("octavos", []):
        if equipo in fase_real.get("Octavos", []):
            pts_8vos += 9

    for equipo in fase_p.get("cuartos", []):
        if equipo in fase_real.get("Cuartos", []):
            pts_4tos += 13

    for equipo in fase_p.get("semifinales", []):
        if equipo in fase_real.get("Semifinales", []):
            pts_sf += 16

    for equipo in fase_p.get("finalistas", []):
        if equipo in fase_real.get("Finalistas", []):
            pts_f += 17

    # =========================
    # PREMIOS
    # =========================

    pts_camp = 14 if premios_p.get("campeon") == reales["premios"].get("Campeón") else 0

    pts_sub = 14 if premios_p.get("subcampeon") == reales["premios"].get("Subcampeón") else 0

    pts_3ro_puesto = (
        16
        if premios_p.get("tercero") == reales["premios"].get("3er puesto")
        else 0
    )

    pts_4to = (
        15
        if premios_p.get("cuarto") == reales["premios"].get("4to puesto")
        else 0
    )

    pts_mg = (
        15
        if premios_p.get("maximo_goleador") == reales["premios"].get("Máximo goleador")
        else 0
    )

    pts_go = (
        15
        if premios_p.get("guante_oro") == reales["premios"].get("Guante de Oro")
        else 0
    )

    # =========================
    # TOTAL
    # =========================

    total = (
        pts_1x2
        + pts_score
        + pts_1ro
        + pts_2do
        + pts_3ro
        + pts_16vos
        + pts_8vos
        + pts_4tos
        + pts_sf
        + pts_f
        + pts_4to
        + pts_3ro_puesto
        + pts_sub
        + pts_camp
        + pts_mg
        + pts_go
    )

    return {
        "1X2": pts_1x2,
        "Score": pts_score,
        "1º": pts_1ro,
        "2º": pts_2do,
        "3º": pts_3ro,
        "16vos": pts_16vos,
        "8vos": pts_8vos,
        "4tos": pts_4tos,
        "SF": pts_sf,
        "F": pts_f,
        "4to": pts_4to,
        "3ro": pts_3ro_puesto,
        "Sub": pts_sub,
        "Camp": pts_camp,
        "MG": pts_mg,
        "GO": pts_go,
        "TOTAL": total
    }