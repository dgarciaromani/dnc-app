import streamlit as st
import pandas as pd
from src.data.database_utils import get_linkedin_courses
from src.utils.linkedin_utils import show_course_details_dialog, show_add_course_dialog

# Authentication check
if not st.session_state.get("authenticated", False):
    st.error("❌ Acceso no autorizado. Por favor, inicie sesión.")
    st.stop()

# Make page use full width
st.set_page_config(layout="wide")
st.title("Cursos LinkedIn")

# Load data
linkedin_courses = get_linkedin_courses()
df = pd.DataFrame(linkedin_courses)

# Display only if there is data
if not df.empty:
    # Add some summary statistics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🌐 Total de Cursos LinkedIn", len(df), border=True)
    with col2:
        total_associations = df["Número de Actividades Asociadas"].sum()
        st.metric("🎯 Total de Asociaciones LinkedIn - Matriz", int(total_associations), border=True)

    # Add Course Button
    if st.button("➕ Agregar Curso", type="primary"):
        st.session_state.show_add_course_dialog = True

    # Initialize session state for selected course
    if "selected_course_idx" not in st.session_state:
        st.session_state.selected_course_idx = None

    # Display the dataframe with row selection
    event = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": None,
            "URN": None,
            "Actividades Formativas Asociadas": None,
            "URL": st.column_config.LinkColumn(
                "URL",
                display_text="Ver Curso",
                help="Haz clic para abrir el curso en LinkedIn",
                width="small"
            ),
            "Número de Actividades Asociadas": st.column_config.NumberColumn(
                "Actividades Asociadas",
                help="Selecciona la fila para ver las actividades asociadas",
                width="medium"
            )
        },
        selection_mode="single-row",
        on_select="rerun"
    )

    # Show dialog when a row is selected
    if event and event.selection and event.selection.rows:
        selected_idx = event.selection.rows[0]
        selected_row = df.iloc[selected_idx]

        # Show the course details dialog
        show_course_details_dialog(selected_row)

    # Instructions
    if not (event and event.selection and event.selection.rows):
        st.info("👆 Haz clic en cualquier fila para ver las actividades formativas asociadas al curso.")

    # Add Course Dialog
    if st.session_state.get("show_add_course_dialog", False):
        show_add_course_dialog()

else:
    st.info("No hay cursos de LinkedIn en la base de datos.")
    st.markdown("""
    Los cursos de LinkedIn aparecerán aquí cuando:
    1. Se complete el Cuestionario DNC.
    2. Se genere una Matriz de Necesidades de Aprendizaje.
    3. Se asocien cursos de LinkedIn a las actividades formativas de la Matriz.
    """)
