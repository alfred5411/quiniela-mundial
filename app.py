import streamlit as st
import json
import pandas as pd
import os

from logica import calcular_puntos_participante_json
from collections import defaultdict

ADMIN_PASSWORD = "GreyArya2026"

st.set_page_config(
    page_title="Quiniela Mundial",
    layout="centered"
)

# st.title("🏆 Pronósticos Mundial CAN-USA-MEX")

st.markdown("""
<style>
.responsive-title {
    font-size: clamp(1.5rem, 5vw, 2.8rem);
    text-align: left;
    font-weight: 700;
}
</style>

<h2 class="responsive-title">🏆 Pronósticos Mundial CAN-USA-MEX</h2>
""", unsafe_allow_html=True)

# MENÚ LATERAL
st.sidebar.title("🏆 Quiniela Mundial")

modo = st.sidebar.radio(
    "Menú",
    [
        "Clasificación",
        "Resultados",
        "Administración"
    ]
)

# CARGA DE DATOS
with open("dataweb/participantes.json", encoding="utf-8") as f:
    participantes = json.load(f)

with open("dataweb/resultados_reales.json", encoding="utf-8") as f:
    reales = json.load(f)

with open("dataweb/jugadores55-26.json", encoding="utf-8") as f:
    jugadores = json.load(f)

# Guardar histórico
def guardar_historico_clasificacion(participantes, reales):

    ranking = []

    for nombre, datos in participantes.items():

        puntos = calcular_puntos_participante_json(
            datos,
            reales
        )["TOTAL"]

        ranking.append(
            {
                "Participante": nombre,
                "Puntos": puntos
            }
        )

    ranking = sorted(
        ranking,
        key=lambda x: x["Puntos"],
        reverse=True
    )

    posiciones = {}

    for i, fila in enumerate(
        ranking,
        start=1
    ):
        posiciones[
            fila["Participante"]
        ] = i

    with open(
        "dataweb/clasificacion_anterior.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            posiciones,
            f,
            ensure_ascii=False,
            indent=2
        )

# Guardar columna CAMBIOS
def guardar_cambios(
    participantes,
    reales
):

    ruta_historico = "dataweb/clasificacion_anterior.json"

    # Leer posiciones anteriores
    if os.path.exists(ruta_historico):

        with open(
            ruta_historico,
            "r",
            encoding="utf-8"
        ) as f:

            posiciones_anteriores = json.load(f)

    else:
        posiciones_anteriores = {}

    # Calcular ranking actual
    ranking = []

    for nombre, datos in participantes.items():

        puntos = calcular_puntos_participante_json(
            datos,
            reales
        )["TOTAL"]

        ranking.append(
            {
                "Participante": nombre,
                "Puntos": puntos
            }
        )

    ranking = sorted(
        ranking,
        key=lambda x: (-x["Puntos"], x["Participante"])
    )

    posiciones_actuales = {}

    for i, fila in enumerate(ranking, start=1):

        posiciones_actuales[
            fila["Participante"]
        ] = i

    cambios = {}

    for nombre, actual in posiciones_actuales.items():

        if nombre in posiciones_anteriores:

            anterior = posiciones_anteriores[nombre]

            diferencia = anterior - actual

            if diferencia > 0:
                cambios[nombre] = f"↑{diferencia}"

            elif diferencia < 0:
                cambios[nombre] = f"↓{abs(diferencia)}"

            else:
                cambios[nombre] = "="

        else:
            cambios[nombre] = "•"

    with open(
        "dataweb/cambios.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            cambios,
            f,
            ensure_ascii=False,
            indent=2
        )        

# Eliminar duplicados en Fase Final
def opciones_disponibles(lista_base, seleccionados):

    usados = [x for x in seleccionados if x]

    return [
        equipo
        for equipo in lista_base
        if equipo not in usados
    ]

# RESUMEN RESULTADOS
def resumen_pronosticos_partido(participantes, numero_partido):

    resumen = defaultdict(list)

    for nombre, datos in participantes.items():

        partidos = datos.get("partidos", [])

        if numero_partido < 1 or numero_partido > len(partidos):
            continue

        partido = partidos[numero_partido - 1]

        if len(partido) < 6:
            continue

        marcador = f"{partido[3]}-{partido[4]}"

        resumen[marcador].append(nombre)

    resumen_ordenado = dict(
        sorted(
            resumen.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
    )

    return resumen_ordenado    

# Crear lista de equipos
equipos = sorted(
    list(
        set(
            p[2] for p in reales["partidos"]
        ).union(
            set(
                p[5] for p in reales["partidos"]
            )
        )
    )
)    

# Posición jugadores
porteros = []
jugadores_campo = []

for j in jugadores:

    posicion = (
        j.get("posición")
        or j.get("posicion")
        or ""
    ).lower()

    nombre = j.get("nombre", "")

    if not nombre:
        continue

    if posicion == "portero":
        porteros.append(nombre)
    else:
        jugadores_campo.append(nombre)

porteros = sorted(porteros)
jugadores_campo = sorted(jugadores_campo)

# BLOQUE CLASIFICACIÓN
if modo == "Clasificación":

    #st.title("🏆 Clasificación General")

    st.markdown("""
    <style>
    .responsive-title {
        font-size: clamp(1.5rem, 5vw, 2.8rem);
        text-align: left;
        font-weight: 700;
    }
    </style>

    <h3 class="responsive-title">🏆 Clasificación General</h3>
    """, unsafe_allow_html=True)

    ranking = []

    for nombre, participante in participantes.items():

        puntos = calcular_puntos_participante_json(
            participante,
            reales
        )

        ranking.append({
            "Participante": nombre,
            "Puntos": puntos["TOTAL"]
        })

    ranking.sort(
        key=lambda x: x["Puntos"],
        reverse=True
    )

    # Crear posiciones actuales
    posiciones_actuales = {}

    for i, fila in enumerate(ranking, start=1):
        posiciones_actuales[fila["Participante"]] = i

    # Leer clasificación anterior
    ruta_historico = "dataweb/clasificacion_anterior.json"

    if os.path.exists(ruta_historico):

        with open(ruta_historico, "r", encoding="utf-8") as f:
            posiciones_anteriores = json.load(f)

    else:
        posiciones_anteriores = {}

    # Leer CAMBIOS
    with open(
        "dataweb/cambios.json",
        "r",
        encoding="utf-8"
    ) as f:

        cambios = json.load(f)    

    # Columna Posición
    for i, fila in enumerate(ranking, start=1):

        if i == 1:
            pos = "🥇 1"
        elif i == 2:
            pos = "🥈 2"
        elif i == 3:
            pos = "🥉 3"
        else:
            pos = str(i)

        fila["Pos"] = pos

        fila["Cambio"] = cambios.get(
            fila["Participante"],
            ""
        )

    # Crear DataFrame    
    df = pd.DataFrame(ranking)
    
    # Reordenar columnas
    df = df[
        [
            "Pos",
            "Cambio",
            "Participante",
            "Puntos"
        ]
    ]

    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )

    # Guardar el histórico
    with open(
        ruta_historico,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            posiciones_actuales,
            f,
            ensure_ascii=False,
            indent=2
        )

    # Mantener Clasificación
    nombres = sorted(
        participantes.keys()
    )

    seleccionado = st.selectbox(
        "Ver participante",
        [""] + nombres
    )

    # Calcular detalle
    if seleccionado:

        detalle = calcular_puntos_participante_json(
            participantes[seleccionado],
            reales
        )

        # Mostrar desglose
        st.subheader(
            f"📊 {seleccionado}"
        )

        st.write(
            f"1X2: {detalle['1X2']}"
        )

        st.write(
            f"Score: {detalle['Score']}"
        )

        st.write(
            f"1º Grupo: {detalle['1º']}"
        )

        st.write(
            f"2º Grupo: {detalle['2º']}"
        )

        st.write(
            f"3º Grupo: {detalle['3º']}"
        )

        st.write(
            f"16vos: {detalle['16vos']}"
        )

        st.write(
            f"8vos: {detalle['8vos']}"
        )

        st.write(
            f"4tos: {detalle['4tos']}"
        )

        st.write(
            f"Semifinales: {detalle['SF']}"
        )

        st.write(
            f"Finalistas: {detalle['F']}"
        )

        st.write(
            f"Campeón: {detalle['Camp']}"
        )

        st.write(
            f"Subcampeón: {detalle['Sub']}"
        )

        st.write(
            f"3er puesto: {detalle['3ro']}"
        )

        st.write(
            f"4º puesto: {detalle['4to']}"
        )

        st.write(
            f"Máximo goleador: {detalle['MG']}"
        )

        st.write(
            f"Guante de Oro: {detalle['GO']}"
        )

        st.metric(
            "TOTAL",
            detalle["TOTAL"]
        )

# BLOQUE RESULTADOS
elif modo == "Resultados":

    st.header("📋 Resultados oficiales")

    seccion = st.selectbox(
        "Mostrar",
        [
            "Partidos",
            "Clasificados por grupo",
            "Fase Final",
            "Premios"
        ]
    )

    # Partidos
    if seccion == "Partidos":

        df = pd.DataFrame(
            reales["partidos"],
            columns=[
                "Nº",
                "Grupo",
                "Equipo 1",
                "M1",
                "M2",
                "Equipo 2"
            ]
        )

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

        st.divider()

        opciones = [
            f"{fila[0]}. {fila[2]} - {fila[5]}"
            for fila in reales["partidos"]
        ]

        partido_sel = st.selectbox(
            "🔍 Ver pronósticos del partido",
            opciones,
            index=None,
            placeholder="Selecciona un partido..."
        )

        if partido_sel:

            numero = int(partido_sel.split(".")[0])

            resumen = resumen_pronosticos_partido(
                participantes,
                numero
            )

            partido_real = reales["partidos"][numero-1]

            st.subheader(
                f"{partido_real[2]} {partido_real[3]} - {partido_real[4]} {partido_real[5]}"
            )

            acierto = f"{partido_real[3]}-{partido_real[4]}"

            if acierto in resumen:

                st.success(
                    f"🎯 Acierto exacto: {len(resumen[acierto])} participantes"
                )

            else:

                st.info("🎯 Nadie acertó el resultado exacto")

            medallas = ["🥇", "🥈", "🥉"]

            for i, (resultado, lista) in enumerate(resumen.items()):

                if i < 3:
                    titulo = medallas[i]
                else:
                    titulo = "⚽"

                with st.expander(
                    f"{titulo} {resultado} ({len(lista)})"
                ):

                    for participante in sorted(lista):

                        st.write(participante)

    # Clasificados por grupo
    elif seccion == "Clasificados por grupo":

        filas = []

        for grupo, equipos in reales["clasificados"].items():

            filas.append(
                {
                    "Grupo": grupo,
                    "1º": equipos[0],
                    "2º": equipos[1],
                    "3º": equipos[2]
                }
            )

        df = pd.DataFrame(filas)

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

    # Fase Final
    elif seccion == "Fase Final":

        for fase, equipos in reales["fase_final"].items():

            st.subheader(fase)

            df = pd.DataFrame(
                {
                    "Posición": range(
                        1,
                        len(equipos) + 1
                    ),
                    "Equipo": equipos
                }
            )

            st.dataframe(
                df,
                width="stretch",
                hide_index=True
            )

    # Premios
    elif seccion == "Premios":

        filas = []

        for k, v in reales["premios"].items():

            filas.append(
                {
                    "Categoría": k,
                    "Selección": v
                }
            )

        df = pd.DataFrame(filas)

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )                           

# BLOQUE ADMINISTRACIÓN
elif modo == "Administración":

    st.title("🔒 Administración")

    password = st.text_input(
        "Contraseña",
        type="password"
    )

    if password != ADMIN_PASSWORD:

        st.warning("Introduce la contraseña de administrador")
        st.stop()

    # Submenú Admin
    seccion_admin = st.radio(
        "Sección",
        [
            "Resultados",
            "Clasificados",
            "Fase Final",
            "Premios"
        ]
    )

    # RESULTADOS
    if seccion_admin == "Resultados":

        st.subheader("⚽ Resultados Reales")

        df = pd.DataFrame(
            reales["partidos"],
            columns=[
                "Nº",
                "Grupo",
                "Equipo 1",
                "M1",
                "M2",
                "Equipo 2"
            ]
        )

        editado = st.data_editor(
            df,
            use_container_width=True,
            num_rows="fixed"
        )

        if st.button("💾 Guardar Resultados"):

            guardar_historico_clasificacion(
                participantes,
                reales
            )

            reales["partidos"] = editado.values.tolist()

            guardar_cambios(
                participantes,
                reales
            )

            with open(
                "dataweb/resultados_reales.json",
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    reales,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            st.success("Resultados guardados")

    # CLASIFICADOS
    elif seccion_admin == "Clasificados":

        st.subheader("🏅 Clasificados por Grupo")

        datos = []

        # Crear diccionario grupo -> equipos
        equipos_por_grupo = {}

        for partido in reales["partidos"]:

            grupo = partido[1]
            eq1 = partido[2]
            eq2 = partido[5]

            if grupo not in equipos_por_grupo:
                equipos_por_grupo[grupo] = set()

            equipos_por_grupo[grupo].add(eq1)
            equipos_por_grupo[grupo].add(eq2)

        for grupo in sorted(reales["clasificados"].keys()):

            st.markdown(f"### Grupo {grupo}")

            opciones = [""] + sorted(list(equipos_por_grupo[grupo]))

            clasif_actual = reales["clasificados"][grupo]

            c1 = st.selectbox(
                "1º",
                opciones,
                index=opciones.index(clasif_actual[0]) if clasif_actual[0] in opciones else 0,
                key=f"{grupo}_1"
            )

            c2 = st.selectbox(
                "2º",
                opciones,
                index=opciones.index(clasif_actual[1]) if clasif_actual[1] in opciones else 0,
                key=f"{grupo}_2"
            )

            c3 = st.selectbox(
                "3º",
                opciones,
                index=opciones.index(clasif_actual[2]) if len(clasif_actual) > 2 and clasif_actual[2] in opciones else 0,
                key=f"{grupo}_3"
            )

        if st.button("💾 Guardar Clasificados"):

            nuevos = {}

            for grupo in sorted(reales["clasificados"].keys()):

                nuevos[grupo] = [
                    st.session_state[f"{grupo}_1"],
                    st.session_state[f"{grupo}_2"],
                    st.session_state[f"{grupo}_3"]
                ]

            guardar_historico_clasificacion(
                participantes,
                reales
            )

            reales["clasificados"] = nuevos

            guardar_cambios(
                participantes,
                reales
            )

            with open(
                "dataweb/resultados_reales.json",
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    reales,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            st.success("Clasificados guardados correctamente")

    # FASE FINAL
    elif seccion_admin == "Fase Final":

        st.subheader("🏆 Fase Final")

        # Equipos clasificados desde la pantalla anterior
        equipos_octavos = []

        for grupo, clasificados in reales["clasificados"].items():
            equipos_octavos.extend(
                [e for e in clasificados if e]
            )

        equipos_octavos = sorted(list(set(equipos_octavos)))

        fase = reales["fase_final"]

        # OCTAVOS
        st.markdown("### Octavos de Final")

        octavos = []

        for i in range(16):

            actual = fase["Octavos"][i]

            disponibles = (
                [""] +
                opciones_disponibles(
                    equipos_octavos,
                    octavos
                )
            )

            if actual and actual not in disponibles:
                disponibles.append(actual)

            equipo = st.selectbox(
                f"Octavos {i+1}",
                disponibles,
                index=(
                    disponibles.index(actual)
                    if actual in disponibles
                    else 0
                ),
                key=f"oct_{i}"
            )

            octavos.append(equipo)

        # CUARTOS
        st.markdown("### Cuartos de Final")

        equipos_cuartos = sorted(
            list(set([e for e in octavos if e]))
        )

        cuartos = []

        for i in range(8):

            actual = fase["Cuartos"][i]

            disponibles = (
                [""] +
                opciones_disponibles(
                    equipos_cuartos,
                    cuartos
                )
            )

            if actual and actual not in disponibles:
                disponibles.append(actual)

            equipo = st.selectbox(
                f"Cuartos {i+1}",
                disponibles,
                index=(
                    disponibles.index(actual)
                    if actual in disponibles
                    else 0
                ),
                key=f"cua_{i}"
            )

            cuartos.append(equipo)

        # SEMIFINALES
        st.markdown("### Semifinales")

        equipos_semis = sorted(
            list(set([e for e in cuartos if e]))
        )

        semis = []

        for i in range(4):

            actual = fase["Semifinales"][i]

            disponibles = (
                [""] +
                opciones_disponibles(
                    equipos_semis,
                    semis
                )
            )

            if actual and actual not in disponibles:
                disponibles.append(actual)

            equipo = st.selectbox(
                f"Semifinales {i+1}",
                disponibles,
                index=(
                    disponibles.index(actual)
                    if actual in disponibles
                    else 0
                ),
                key=f"sem_{i}"
            )

            semis.append(equipo)    

        # FINALISTAS
        st.markdown("### Finalistas")

        equipos_finalistas = sorted(
            list(set([e for e in semis if e]))
        )

        finalistas = []

        for i in range(2):

            actual = fase["Finalistas"][i]

            disponibles = (
                [""] +
                opciones_disponibles(
                    equipos_finalistas,
                    finalistas
                )
            )

            if actual and actual not in disponibles:
                disponibles.append(actual)

            equipo = st.selectbox(
                f"Finalistas {i+1}",
                disponibles,
                index=(
                    disponibles.index(actual)
                    if actual in disponibles
                    else 0
                ),
                key=f"fin_{i}"
            )

            finalistas.append(equipo)    

        if st.button("💾 Guardar Fase Final"):

            guardar_historico_clasificacion(
                participantes,
                reales
            )

            reales["fase_final"]["Octavos"] = octavos
            reales["fase_final"]["Cuartos"] = cuartos
            reales["fase_final"]["Semifinales"] = semis
            reales["fase_final"]["Finalistas"] = finalistas

            guardar_cambios(
                participantes,
                reales
            )

            with open(
                "dataweb/resultados_reales.json",
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    reales,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            st.success("Fase final guardada correctamente")
    
    # PREMIOS
    elif seccion_admin == "Premios":

        st.subheader("🎖 Premios")

        premios = reales["premios"]

        finalistas = sorted(
            list(
                set(
                    [
                        e
                        for e in reales["fase_final"]["Finalistas"]
                        if e
                    ]
                )
            )
        )

        semifinalistas = sorted(
            list(
                set(
                    [
                        e
                        for e in reales["fase_final"]["Semifinales"]
                        if e
                    ]
                )
            )
        )

        equipos_3y4 = [
            e
            for e in semifinalistas
            if e not in finalistas
        ]


        seleccionados = []

        # Campeón
        disponibles = [""] + [
            e for e in finalistas
        ]

        campeon = st.selectbox(
            "Campeón",
            disponibles,
            index=(
                disponibles.index(
                    premios.get("Campeón", "")
                )
                if premios.get("Campeón", "") in disponibles
                else 0
            )
        )

        if campeon:
            seleccionados.append(campeon)

        # Subcampeón    
        disponibles = [""] + [
            e for e in finalistas
            if e not in seleccionados
        ]

        actual = premios.get("Subcampeón", "")

        if actual and actual not in disponibles:
            disponibles.append(actual)

        subcampeon = st.selectbox(
            "Subcampeón",
            disponibles,
            index=(
                disponibles.index(actual)
                if actual in disponibles
                else 0
            )
        )

        if subcampeon:
            seleccionados.append(subcampeon)

        # 3ER PUESTO
        opciones_3ro = [""] + equipos_3y4

        tercero = st.selectbox(
            "3er puesto",
            opciones_3ro,
            index=(
                opciones_3ro.index(premios.get("3er puesto", ""))
                if premios.get("3er puesto", "") in opciones_3ro
                else 0
            )
        )

        if tercero:
            seleccionados.append(tercero)

        # 4TO PUESTO
        opciones_4to = [""] + [
            e for e in equipos_3y4
            if e != tercero
        ]

        actual = premios.get("4to puesto", "")

        if actual and actual not in opciones_4to:
            opciones_4to.append(actual)

        cuarto = st.selectbox(
            "4to puesto",
            opciones_4to,
            index=(
                opciones_4to.index(actual)
                if actual in opciones_4to
                else 0
            )
        )

        if cuarto:
            seleccionados.append(cuarto)

        # Goleador        
        opciones_goleadores = [""] + jugadores_campo

        goleador = st.selectbox(
            "Máximo goleador",
            opciones_goleadores,
            index=opciones_goleadores.index(
                premios.get("Máximo goleador", "")
            ) if premios.get("Máximo goleador", "") in opciones_goleadores else 0
        )

        # Guante de Oro
        opciones_porteros = [""] + porteros

        guante = st.selectbox(
            "Guante de Oro",
            opciones_porteros,
            index=opciones_porteros.index(
                premios.get("Guante de Oro", "")
            ) if premios.get("Guante de Oro", "") in opciones_porteros else 0
        )

        if st.button("💾 Guardar Premios"):

            guardar_historico_clasificacion(
                participantes,
                reales
            )

            reales["premios"] = {
                "Campeón": campeon,
                "Subcampeón": subcampeon,
                "3er puesto": tercero,
                "4to puesto": cuarto,
                "Máximo goleador": goleador,
                "Guante de Oro": guante
            }

            guardar_cambios(
                participantes,
                reales
            )

            #with open(
            #    "dataweb/resultados_reales.json",
            #    "w",
            #    encoding="utf-8"
            #) as f:

            #    json.dump(
            #        reales,
            #        f,
            #        ensure_ascii=False,
            #        indent=2
            #    )

            st.success("Premios guardados")