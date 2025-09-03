import streamlit as st
import pandas as pd
from src.services.linkedin_api import fetch_courses

def get_search_details(df):
    # Instructions box
    st.markdown("""
    Cursos disponibles en el plan de formación (modalidad "Virtual" y fuente "Externa"):
    """)

    df["Estado Curso"] = df["Estado Curso"].apply(lambda x: "✅" if x is not None else "🔍")

    # Load data
    event = st.dataframe(
        df, 
        column_config={
            "Estado Curso": st.column_config.TextColumn(
                "Estado",
                help="Indica si el curso ya ha sido sugerido (✅) o si está pendiente de sugerencia (🔍).",
            )
        },
        column_order=["Estado Curso", "Actividad Formativa", "Objetivo Desempeño", "Contenidos", "Skills", "Keywords", "Audiencia", "Prioridad"],
        use_container_width=True, 
        hide_index=True, 
        key="data", 
        on_select="rerun", 
        selection_mode="single-row"
    )

    # Instructions box
    st.markdown("""
    Usa estas opciones para afinar tu búsqueda:
    """)

    # Let user add more info to params
    results_spanish = st.checkbox("Buscar cursos solamente en Español", value=True, key="results_spanish")
    options_asset_type = [
        ("COURSE", "Cursos"),
        ("VIDEO", "Videos"),
        ("LEARNING_PATH", "Itinerarios de Aprendizaje")
    ]
    selected_asset_type = st.selectbox(
        "Tipo de activo",
        options_asset_type,
        format_func=lambda x: x[1],
        key="asset_type"
    )
    asset_type = selected_asset_type[0]
    options_level = [
        ("ALL", "Todas las audiencias"),
        ("BEGINNER", "Principiante"),
        ("INTERMEDIATE", "Intermedio"),
        ("ADVANCED", "Avanzado")
    ]
    selected_level = st.selectbox(
        "Nivel de dificultad",
        options_level,
        format_func=lambda x: x[1],
        key="level"
    )
    level = selected_level[0]

    st.button("Buscar sugerencia de curso en LinkedIn Learning", on_click=lambda: search_button(event.selection["rows"], df, asset_type, results_spanish, level, options_level))
    
    if not event.selection["rows"]:
        st.warning("Por favor selecciona una fila antes de hacer clic en el botón para buscar sugerencias de cursos en LinkedIn Learning.")

def search_button(rows, df, asset_type, results_spanish, level, options_level):
    if len(rows) > 0:            
        with st.spinner("Buscando cursos en LinkedIn Learning... Por favor espera ⏳"):
            # Extract the skill from the row
            st.session_state.selected_row = df.iloc[rows[0]]
            keywords = st.session_state.selected_row["Keywords"]

            # Fetch courses from LinkedIn Learning
            st.session_state.all_courses, st.session_state.total_linkedin = fetch_courses(keywords, asset_type, 100, results_spanish, level, options_level)

        if st.session_state.total_linkedin != 0: 
            st.session_state.linkedin_results_fail = False
            st.success(f"LinkedIn Learning cuenta con {st.session_state.total_linkedin} resultados que coinciden con tu búsqueda.")               
        else:
            st.session_state.linkedin_results_fail = True
            st.warning("No se encontraron resultados relevantes en LinkedIn Learning. Por favor, ajusta tus criterios de búsqueda.")