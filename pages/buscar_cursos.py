import streamlit as st
import pandas as pd
import json
import time
from utils.database_utils import get_virtual_courses, add_linkedin_course
from utils.linkedin_form import get_search_details
from utils.bedrock_api import get_from_ai, process_response

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
        st.info("No hay cursos en tu plan que sean virtuales y externos.")
    else:
        get_search_details(df)

# Step 2: Select a course from LinkedIn
else:
    # Reset all
    if st.button("Reiniciar búsqueda"):
        st.session_state.clear()
        st.rerun()

    with st.expander(f"Mostrando resultados para: '{st.session_state.selected_row['Actividad Formativa']}' (ver más información)"):
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
        if st.session_state.total_linkedin > 500:
            st.info("Hay demasiados resultados, por lo que te recomendamos seleccionar aquellos resultados que te interesen antes de hacer clic en el botón 'Recomiéndame con IA!'.")
        
        if st.button("Recomiéndame con IA!"):
            # Check if user has selected specific courses
            has_selection = len(linkedin_results.selection["rows"]) > 0

            if st.session_state.total_linkedin > 500 and not has_selection:
                st.warning("Hay demasiados resultados para procesar. Por favor, ajusta tus criterios de búsqueda o selecciona aquellos resultados que te interesen.")
            elif st.session_state.total_linkedin > 500 and has_selection and len(linkedin_results.selection["rows"]) > 500:
                st.warning("Has seleccionado demasiados cursos para procesar. Por favor, desselecciona algunos cursos e intenta nuevamente.")
            else:
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

                    contents = [json.dumps(filtered_courses, ensure_ascii=False), json.dumps(st.session_state.selected_row.to_dict(), ensure_ascii=False)]

                    # Get recommendations from AI
                    recommendations_response = get_from_ai(prompt, contents)
                    st.session_state.recommendations = process_response(recommendations_response)

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
            selection_mode="single-row")
        
        if len(ia_results.selection["rows"]) > 0:
            if st.button("Agregar a Plan de Formación"):
                selection = recommendations_df.iloc[ia_results.selection["rows"][0]]
                add_linkedin_course(selection, st.session_state.selected_row['id'])
                st.success(f"El curso '{selection['Title']}' ha sido agregado al plan de formación.")
                time.sleep(5)
                st.session_state.clear()
                st.rerun()