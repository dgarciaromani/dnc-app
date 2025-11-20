import streamlit as st
import pandas as pd
from src.data.database_utils import get_virtual_courses
from src.forms.linkedin_form import get_search_details
from src.auth.authentication import stay_authenticated
from src.utils.buscar_utils import show_course_filters, show_ai_recommendation_dialog, MAX_LINKEDIN_ROWS_FOR_AI
from src.utils.download_utils import download_excel_button

# Authentication check
if not st.session_state.get("authenticated", False):
    st.error("❌ Acceso no autorizado. Por favor, inicie sesión.")
    st.stop()

# Make page use full width
st.set_page_config(layout="wide")

# Initialize session state to control results
if "selected_row" not in st.session_state:
    st.session_state.selected_row = None

if "linkedin_results_fail" not in st.session_state:
    st.session_state.linkedin_results_fail = False

if "all_courses" not in st.session_state:
    st.session_state.all_courses = []

if "total_linkedin" not in st.session_state:
    st.session_state.total_linkedin = 0

if "show_recommendations_button" not in st.session_state:
    st.session_state.show_recommendations_button = False  

if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

if "ai_already_run" not in st.session_state:
    st.session_state.ai_already_run = False

if "ai_selection_used" not in st.session_state:
    st.session_state.ai_selection_used = []


# Step 1: Select a row from the table
if st.session_state.selected_row is None or st.session_state.linkedin_results_fail:

    st.title("Buscar Cursos de LinkedIn Learning")

    # Instructions box
    st.markdown("""
    Para sugerir cursos de LinkedIn Learning, selecciona una fila de la tabla, afina tu búsqueda y haz clic en el botón "Buscar sugerencia de curso en LinkedIn Learning".
    """)

    # Load data
    data = get_virtual_courses()
    df = pd.DataFrame(data)

    # Display only if there is data
    if df.empty:
        st.info("No hay cursos en tu matriz que sean virtuales y externos.")
    else:
        # Filters section with expander
        with st.expander("🔍 Filtros", expanded=False):
            show_course_filters(df)

        # Apply filters to dataframe
        filtered_df = df.copy()

        # Apply each filter if selections exist
        for column, selected_values in st.session_state.get("course_filters", {}).items():
            if selected_values:  # Only filter if values are selected
                if column == "Estado":
                    # Special handling for Estado filter
                    estado_col = "Estado Curso"
                    if "Con cursos asociados" in selected_values and "Sin cursos asociados" in selected_values:
                        # Both selected - show all rows
                        pass
                    elif "Con cursos asociados" in selected_values:
                        # Only show rows with courses
                        filtered_df = filtered_df[filtered_df[estado_col].notna() & (filtered_df[estado_col] != "")]
                    elif "Sin cursos asociados" in selected_values:
                        # Only show rows without courses
                        filtered_df = filtered_df[filtered_df[estado_col].isna() | (filtered_df[estado_col] == "")]
                else:
                    # Normal filter logic for other columns
                    actual_column = column
                    if actual_column in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df[actual_column].isin(selected_values)]

        # Display filtered dataframe with record count
        if not filtered_df.empty:
            st.markdown(f"**Mostrando {len(filtered_df)} de {len(df)} registros**")
            get_search_details(filtered_df)
        else:
            st.info("No hay registros que coincidan con los filtros seleccionados.")
            if st.button("↩️ Mostrar todos los registros", type="primary"):
                st.session_state.course_filters = {}
                st.rerun()

# Step 2: Select a course from LinkedIn
else:
    # Reset all
    if st.button("↩️ Reiniciar búsqueda", type="primary"):
        user_data = {
                    "name": st.session_state.name,
                    "role": st.session_state.role,
                    "username": st.session_state.username
                }
        st.session_state.clear()
        stay_authenticated(user_data["name"], user_data["role"], user_data["username"])
        st.rerun()

    with st.expander(f"Mostrando resultados para: '{st.session_state.selected_row['Actividad Formativa']}' (ver más información)"):
        st.text(f"Gerencia: '{st.session_state.selected_row['Gerencia']}'")
        st.text(f"Objetivo de desempeño: '{st.session_state.selected_row['Objetivo Desempeño']}'")
        st.text(f"Contenidos: '{st.session_state.selected_row['Contenidos']}'")
        st.text(f"Skills: '{st.session_state.selected_row['Skills']}'")
        st.text(f"Keywords: '{st.session_state.selected_row['Keywords']}'")
        st.text(f"Audiencia: '{st.session_state.selected_row['Audiencia']}'")
        st.text(f"Prioridad: '{st.session_state.selected_row['Prioridad']}'")
    
    st.title(f"Resultados LinkedIn Learning ({st.session_state.total_linkedin})")

    if st.session_state.total_linkedin != 0:
        st.markdown("""
        A continuación se muestran los resultados obtenidos desde LinkedIn Learning. Para obtener recomendaciones, presiona el botón "Recomiéndame con IA!" o selecciona aquellos cursos que te interesen más para analizar cuál recomendarte.
        """)
        courses_df = pd.DataFrame(st.session_state.all_courses)
        courses_df["Title"] = courses_df["Title"].str.strip()
        linkedin_results = st.dataframe(
            courses_df, 
            use_container_width=True, 
            hide_index=True, 
            on_select="rerun", 
            selection_mode="multi-row")
        st.session_state.show_recommendations_button = True

    if st.session_state.show_recommendations_button:
        if st.session_state.total_linkedin > MAX_LINKEDIN_ROWS_FOR_AI:
            st.info(f"Hay demasiados resultados (más de {MAX_LINKEDIN_ROWS_FOR_AI}), por lo que te recomendamos seleccionar aquellos resultados que te interesen antes de hacer clic en el botón 'Recomiéndame con IA!'.")

        # Download button for search results
        selected_rows = linkedin_results.selection.get("rows", [])
        if selected_rows:
            row_count = len(selected_rows)
            download_data = courses_df.iloc[selected_rows]
            filename = f"cursos_linkedin_seleccionados_{row_count}_filas.xlsx"
        else:
            row_count = len(courses_df)
            download_data = courses_df
            filename = f"cursos_linkedin_todos_{row_count}_filas.xlsx"

        download_excel_button(
            download_data,
            filename=filename,
            button_text_prefix="📥 Descargar resultados"
        )

        # AI recommendation button
        if st.button("✨ Recomiéndame con IA!", type="primary"):
            show_ai_recommendation_dialog(courses_df, linkedin_results, st.session_state.selected_row)