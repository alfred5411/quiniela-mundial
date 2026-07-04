from github import Github
import streamlit as st
import json


# =====================================
# SUBIR UN JSON AL REPOSITORIO
# =====================================

def subir_json(ruta_repo, datos, mensaje_commit=None):
    """
    Guarda un diccionario como JSON en GitHub.

    ruta_repo:
        Ej: dataweb/resultados_reales.json

    datos:
        Diccionario que se quiere guardar

    mensaje_commit:
        Opcional.
    """

    token = st.secrets["GITHUB_TOKEN"]

    g = Github(token)

    repo = g.get_repo("alfred5411/quiniela-mundial")

    if mensaje_commit is None:
        mensaje_commit = f"Actualizar {ruta_repo}"

    contenido = json.dumps(
        datos,
        ensure_ascii=False,
        indent=2
    )

    try:

        archivo = repo.get_contents(ruta_repo)

        repo.update_file(
            path=ruta_repo,
            message=mensaje_commit,
            content=contenido,
            sha=archivo.sha,
            branch="main"
        )

        return True

    except Exception as e:

        print(e)

        return False