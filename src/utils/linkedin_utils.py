import streamlit as st
import pandas as pd
from src.services.linkedin_api import search_course_by_identifier
from src.data.database_utils import get_learning_activities_for_association, add_linkedin_course_manual


def show_course_details_dialog(selected_row):
    """Dialog to show course details and associated activities."""
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


@st.dialog("➕ Agregar Curso de LinkedIn", width="large")
def show_add_course_dialog():
    """Dialog to add a new LinkedIn course."""
    st.markdown("Ingresa el URN del curso de LinkedIn Learning que deseas agregar:")

    # Input field for URN
    course_identifier = st.text_input(
        "URN del curso:",
        placeholder="Ej: urn:li:lyndaCourse:12345",
        help="Ingresa el URN del curso de LinkedIn Learning. Ejemplo: urn:li:lyndaCourse:12345"
    )

    # Search button
    if st.button("🔍 Buscar Curso", type="primary", use_container_width=True):
        if not course_identifier or not course_identifier.strip():
            st.error("Por favor ingresa un URN de curso válido.")
        else:
            with st.spinner("Buscando curso en LinkedIn..."):
                course_data, error = search_course_by_identifier(course_identifier.strip())

                if error:
                    st.error(f"❌ Error: {error}")
                    st.session_state.found_course = None
                else:
                    st.success(f"✅ Curso encontrado: **{course_data['Title']}**")
                    st.session_state.found_course = course_data

    # If course was found, show association options
    if "found_course" in st.session_state and st.session_state.found_course:
        course_data = st.session_state.found_course

        # Display course information
        with st.expander("📋 Ver más información del curso"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Nivel:** {course_data['Level']}")
                st.markdown(f"**Duración:** {course_data['Duration (min)']}")
            with col2:
                st.markdown(f"**URL:** {course_data['URL']}")
            st.markdown(f"**Descripción:** {course_data['Description']}")

        st.markdown("### 🎯 Asociar con Actividades Formativas")

        # Get learning activities
        activities = get_learning_activities_for_association()

        if activities:
            st.markdown("Selecciona las actividades formativas que deseas asociar con este curso:")

            # Initialize selected activities in session state if not exists
            if "selected_activities" not in st.session_state:
                st.session_state.selected_activities = []

            # Create checkboxes for activity selection
            current_selections = []
            for activity in activities:
                activity_display = f"{activity['Actividad Formativa']} ({activity['Gerencia']} - {activity['Audiencia']})"
                # Use session state to maintain checkbox state
                checkbox_key = f"activity_{activity['id']}"
                is_checked = st.checkbox(
                    activity_display,
                    key=checkbox_key,
                    value=activity['id'] in st.session_state.selected_activities
                )
                if is_checked:
                    current_selections.append(activity['id'])

            # Update session state with current selections
            st.session_state.selected_activities = current_selections

            # Submit button
            if st.button("✅ Agregar Curso", type="primary", use_container_width=True):
                if not st.session_state.selected_activities:
                    st.warning("⚠️ Selecciona al menos una actividad formativa para asociar.")
                else:
                    result = add_linkedin_course_manual(
                        course_data,
                        st.session_state.selected_activities
                    )

                    if result["success"]:
                        st.success(result["message"])
                        # Clean up session state
                        st.session_state.show_add_course_dialog = False
                        st.session_state.found_course = None
                        st.session_state.selected_activities = []
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result['message']}")

        else:
            st.warning("⚠️ No hay actividades formativas disponibles para asociar.")
            st.markdown("Primero necesitas crear una Matriz de Necesidades de Aprendizaje.")