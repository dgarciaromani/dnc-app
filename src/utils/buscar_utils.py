import streamlit as st
import json
import pandas as pd
from src.services.bedrock_api import get_from_ai, process_response
from src.utils.download_utils import download_excel_button
from src.data.database_utils import add_linkedin_course
from src.auth.authentication import stay_authenticated
import time

def show_course_filters(df):
    """Display filters for course search page (Estado, Gerencia, Audiencia, Prioridad)"""
    # Create filter columns
    col1, col2, col3, col4 = st.columns(4)

    # Initialize filters if not exists
    if "course_filters" not in st.session_state:
        st.session_state.course_filters = {}

    with col1:
        # Estado filter (Estado Curso) - binary filter: with/without courses
        if "Estado Curso" in df.columns:
            # Check if Estado Curso column has any non-empty values
            has_courses = df["Estado Curso"].notna() & (df["Estado Curso"] != "")
            has_any_courses = has_courses.any()

            if has_any_courses:
                estado_options = ["Con cursos asociados", "Sin cursos asociados"]
            else:
                estado_options = ["Sin cursos asociados"]

            selected_estados = st.multiselect(
                "Estado",
                options=estado_options,
                default=st.session_state.course_filters.get("Estado", []),
                placeholder="Elige un Estado",
                key="estado_course_filter"
            )
            st.session_state.course_filters["Estado"] = selected_estados

    with col2:
        # Gerencia filter
        if "Gerencia" in df.columns:
            gerencias = sorted(df["Gerencia"].dropna().unique())
            selected_gerencias = st.multiselect(
                "Gerencia",
                options=gerencias,
                default=st.session_state.course_filters.get("Gerencia", []),
                placeholder="Elige una Gerencia",
                key="gerencia_course_filter"
            )
            st.session_state.course_filters["Gerencia"] = selected_gerencias

    with col3:
        # Audiencia filter
        if "Audiencia" in df.columns:
            audiencias = sorted(df["Audiencia"].dropna().unique())
            selected_audiencias = st.multiselect(
                "Audiencia",
                options=audiencias,
                default=st.session_state.course_filters.get("Audiencia", []),
                placeholder="Elige una Audiencia",
                key="audiencia_course_filter"
            )
            st.session_state.course_filters["Audiencia"] = selected_audiencias

    with col4:
        # Prioridad filter
        if "Prioridad" in df.columns:
            prioridades = sorted(df["Prioridad"].dropna().unique())
            selected_prioridades = st.multiselect(
                "Prioridad",
                options=prioridades,
                default=st.session_state.course_filters.get("Prioridad", []),
                placeholder="Elige una Prioridad",
                key="prioridad_course_filter"
            )
            st.session_state.course_filters["Prioridad"] = selected_prioridades

    # Clear filters button
    col_clear, col_space = st.columns([1, 3])
    with col_clear:
        if st.button("🗑️ Limpiar Filtros", type="primary"):
            st.session_state.course_filters = {}
            st.rerun()


@st.dialog("🤖 Recomendaciones con IA", width="large")
def show_ai_recommendation_dialog(courses_df, linkedin_results, selected_row):
    """Display AI recommendation dialog with all the logic for course recommendations"""

    # Check if the current selection is different from what was used for AI
    current_selection = linkedin_results.selection["rows"]
    selection_changed = current_selection != st.session_state.ai_selection_used
    
    # If AI has already been run and selection hasn't changed, use existing recommendations
    if st.session_state.ai_already_run and st.session_state.recommendations and not selection_changed:
        st.info("✅ Usando recomendaciones existentes")
        pass  # Skip to the display section below
    else:
        # If selection changed, show a message
        if selection_changed and st.session_state.ai_already_run:
            st.info("🔄 Selección modificada, recalculando recomendaciones con IA...")
        # Continue with AI processing...
        # Check if user has selected specific courses
        has_selection = len(linkedin_results.selection["rows"]) > 0

        if st.session_state.total_linkedin > 500 and not has_selection:
            st.warning("Hay demasiados resultados para procesar. Por favor, ajusta tus criterios de búsqueda o selecciona aquellos resultados que te interesen.")
            return
        elif st.session_state.total_linkedin > 500 and has_selection and len(linkedin_results.selection["rows"]) > 500:
            st.warning("Has seleccionado demasiados cursos para procesar. Por favor, desselecciona algunos cursos e intenta nuevamente.")
            return

        with st.spinner("Analizando recomendaciones con IA... Por favor espera ⏳"):

            # Prepare contents for AI
            prompt = st.secrets["prompt_linkedin"]

            filtered_courses = []

            if len(linkedin_results.selection["rows"]) == 0:
                # Reduce the size of the data sent to IA by iterating over all_courses and selecting only the relevant rows for each dict
                filtered_courses = [
                    {
                        "Title": course.get("Title"),
                        "Description": course.get("Description")
                    }
                    for course in st.session_state.all_courses
                ]
            else:
                filtered_courses = [
                    {
                        "Title": course.get("Title"),
                        "Description": course.get("Description")
                    }
                    for course in st.session_state.all_courses
                    if st.session_state.all_courses.index(course) in linkedin_results.selection["rows"]
                ]

            contents = [json.dumps(filtered_courses, ensure_ascii=False), json.dumps(selected_row.to_dict(), ensure_ascii=False)]

            # Get recommendations from AI
            recommendations_response = get_from_ai(prompt, contents)
            st.session_state.recommendations = process_response(recommendations_response)
            st.session_state.ai_already_run = True  # Mark that AI has been run
            st.session_state.ai_selection_used = current_selection.copy()  # Store the selection used

    if st.session_state.recommendations:
        # Convert to DataFrame and display in Streamlit
        st.success(f"Hay {len(st.session_state.recommendations)} curso(s) recomendado(s).")
        preliminary_df = pd.DataFrame(st.session_state.recommendations)
        preliminary_df["Title"] = preliminary_df["Title"].str.strip()
        recommendations_df = pd.merge(preliminary_df, courses_df, on="Title", how="left")
        ia_results = st.dataframe(
            recommendations_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        # Download button for recommendations
        download_excel_button(
            recommendations_df,
            filename="cursos_linkedin_recomendados.xlsx",
            button_text_prefix="📥 Descargar recomendados"
        )

        if len(ia_results.selection["rows"]) > 0:
            if st.button("➕ Agregar a la Matriz de Necesidades", type="primary"):
                selection = recommendations_df.iloc[ia_results.selection["rows"][0]]
                add_linkedin_course(selection, st.session_state.selected_row['id'])
                st.success(f"El curso '{selection['Title']}' ha sido agregado a la matriz de necesidades.")
                time.sleep(5)
                user_data = {
                    "name": st.session_state.name,
                    "role": st.session_state.role,
                    "username": st.session_state.username
                }
                st.session_state.clear()
                stay_authenticated(user_data["name"], user_data["role"], user_data["username"])
                st.rerun()

    else:
        st.info("No se pudieron generar recomendaciones con IA. Inténtalo de nuevo.")

