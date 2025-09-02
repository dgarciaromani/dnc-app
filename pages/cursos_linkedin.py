import streamlit as st
import pandas as pd
from utils.database_utils import get_linkedin_courses

# Make page use full width
st.set_page_config(layout="wide")
st.title("Cursos de LinkedIn")

# Load data
linkedin_courses = get_linkedin_courses()
df = pd.DataFrame(linkedin_courses)

# Display only if there is data
if not df.empty:
    # Add some summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Cursos", len(df))
    with col2:
        total_associations = df["Número de Actividades Asociadas"].sum()
        st.metric("Total de Asociaciones", int(total_associations))
    with col3:
        courses_with_associations = len(df[df["Número de Actividades Asociadas"] > 0])
        st.metric("Cursos Asociados", courses_with_associations)

    st.markdown("---")

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

        # Create dialog function
        @st.dialog(f"📋 {selected_row['Nombre del Curso']}", width="large")
        def show_course_details():
            # Show activities or message
            if selected_row["Número de Actividades Asociadas"] > 0:
                st.markdown("### 📝 Actividades Formativas Asociadas:")

                if pd.notna(selected_row["Actividades Formativas Asociadas"]) and selected_row["Actividades Formativas Asociadas"].strip():
                    activities = selected_row["Actividades Formativas Asociadas"].split("; ")
                    for i, activity in enumerate(activities, 1):
                        if activity.strip():
                            st.markdown(f"**{i}.** {activity.strip()}")
                st.markdown("---")
                st.markdown(f"[🔗 Ver curso en LinkedIn]({selected_row['URL']})")
            
            else:
                st.info("🚫 Este curso no tiene actividades formativas asociadas.")
                if pd.notna(selected_row["URL"]):
                    st.markdown("Puedes acceder directamente al curso usando el enlace arriba.")

        # Show the dialog
        show_course_details()

    # Instructions
    if not (event and event.selection and event.selection.rows):
        st.markdown("💡 **Tip:** Haz clic en cualquier fila para ver las actividades formativas asociadas al curso.")

else:
    st.info("No hay cursos de LinkedIn en la base de datos.")
    st.markdown("""
    Los cursos de LinkedIn aparecerán aquí cuando:
    1. Se complete el Cuestionario DNC.
    2. Se genere un Plan de Formación.
    3. Se asocien cursos de LinkedIn a las actividades formativas del Plan.
    """)
