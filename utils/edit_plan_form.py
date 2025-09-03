import streamlit as st
from utils.database_utils import fetch_all

# Fetch lookup tables from DB
gerencias = fetch_all("gerencias")
subgerencias = fetch_all("subgerencias")
areas = fetch_all("areas")
desafios = fetch_all("desafios")
audiencias = fetch_all("audiencias")
modalidades = fetch_all("modalidades")
fuentes = fetch_all("fuentes")
prioridades = fetch_all("prioridades")
linkedin = fetch_all("linkedin_courses")


def get_row_data(row_data):
    with st.form("edit_row_form"):
        
        # Gerencia dropdown
        gerencia_options = [name for name, id in gerencias.items()]
        current_gerencia = row_data.get("Gerencia")
        gerencia_index = next((i for i, name in enumerate(gerencia_options) if name == current_gerencia), 0)
        gerencia_selected = st.selectbox(
            "Gerencia (*)",
            options=gerencia_options,
            index=gerencia_index
        )

        # Subgerencia dropdown
        subgerencia_options = [None, "N/A"] + [name for name, id in subgerencias.items()]
        current_subgerencia = row_data.get("Subgerencia")
        subgerencia_index = next((i for i, name in enumerate(subgerencia_options) if name == current_subgerencia), 0)
        subgerencia_selected = st.selectbox(
            "Subgerencia",
            options=subgerencia_options,
            index=subgerencia_index,
            format_func=lambda x: "Selecciona una Subgerencia..." if x is None else x
        )

        # Área dropdown
        area_options = [None, "N/A"] + [name for name, id in areas.items()]
        current_area = row_data.get("Área")
        area_index = next((i for i, name in enumerate(area_options) if name == current_area), 0)
        area_selected = st.selectbox(
            "Área",
            options=area_options,
            index=area_index,
            format_func=lambda x: "Selecciona un Área..." if x is None else x
        )

        # Desafío Estratégico dropdown
        desafio_options = [name for name, id in desafios.items()]
        current_desafio = row_data.get("Desafío Estratégico")
        desafio_index = next((i for i, name in enumerate(desafio_options) if name == current_desafio), 0)
        desafio_selected = st.selectbox(
            "Desafío Estratégico (*)",
            options=desafio_options,
            index=desafio_index
        )

        # Actividad formativa
        actividad_formativa = st.text_input(
            "Actividad Formativa (*)",
            value=str(row_data.get("Actividad Formativa", "")),
            help="Describe la actividad formativa",
        )

        # Objeto Desempeño
        objetivo_desempeno = st.text_area(
            "Objetivo Desempeño (*)",
            value=str(row_data.get("Objetivo Desempeño", "")),
            help="¿Qué cosas deben ocurrir para cumplir este desafío?"
        )

        # Contenidos
        contenidos = st.text_area(
            "Contenidos (*)",
            value=str(row_data.get("Contenidos", "")),
            help="¿Qué le falta al equipo en términos de competencias?"
        )

        # Skills
        skills = st.text_area(
            "Skills (*)",
            value=str(row_data.get("Skills", "")),
            help="Habilidades que se deben desarrollar"
        )

        # Keywords
        keywords = st.text_input(
            "Keywords (*)",
            value=str(row_data.get("Keywords", "")),
            help="Palabras clave para búsqueda de cursos"
        )

        # Audiencia dropdown
        audiencia_options = [name for name, id in audiencias.items()]
        current_audiencia = row_data.get("Audiencia")
        audiencia_index = next((i for i, name in enumerate(audiencia_options) if name == current_audiencia), 0)
        audiencia_selected = st.selectbox(
            "Audiencia (*)",
            options=audiencia_options,
            index=audiencia_index
        )

        # Modalidad dropdown
        modalidad_options = [name for name, id in modalidades.items()]
        current_modalidad = row_data.get("Modalidad")
        modalidad_index = next((i for i, name in enumerate(modalidad_options) if name == current_modalidad), 0)
        modalidad_selected = st.selectbox(
            "Modalidad (*)",
            options=modalidad_options,
            index=modalidad_index
        )

        # Fuente dropdown
        fuente_options = [name for name, id in fuentes.items()]
        current_fuente = row_data.get("Fuente")
        fuente_index = next((i for i, name in enumerate(fuente_options) if name == current_fuente), 0)
        fuente_selected = st.selectbox(
            "Fuente (*)",
            options=fuente_options,
            index=fuente_index
        )

        # Fuente Interna
        fuente_interna = st.text_input(
            "Fuente Interna",
            value=str(row_data.get("Fuente Interna", "")),
            help="¿Quién o dónde está el conocimiento internamente?"
        )

        # Prioridad dropdown
        prioridad_options = [name for name, id in prioridades.items()]
        current_prioridad = row_data.get("Prioridad")
        prioridad_index = next((i for i, name in enumerate(prioridad_options) if name == current_prioridad), 0)
        prioridad_selected = st.selectbox(
            "Prioridad (*)",
            options=prioridad_options,
            index=prioridad_index
        )        

        # LinkedIn course dropdown
        linkedin_options = [None] + [name for name, id in linkedin.items()]
        current_linkedin = row_data.get("Curso Sugerido LinkedIn")
        linkedin_index = next((i for i, name in enumerate(linkedin_options) if name == current_linkedin), 0)
        linkedin_selected = st.selectbox(
            "Curso Sugerido LinkedIn",
            options=linkedin_options,
            index=linkedin_index,
            format_func=lambda x: "Selecciona un curso..." if x is None else x
        )

        # Submit button
        submitted = st.form_submit_button("Guardar cambios")

    return submitted, {
        "gerencia": gerencia_selected,
        "subgerencia": subgerencia_selected,
        "area": area_selected,
        "desafio": desafio_selected,
        "actividad_formativa": actividad_formativa,
        "objetivo_desempeno": objetivo_desempeno,
        "contenidos": contenidos,
        "skills": skills,
        "keywords": keywords,
        "audiencia": audiencia_selected,
        "modalidad": modalidad_selected,
        "fuente": fuente_selected,
        "fuente_interna": fuente_interna,
        "prioridad": prioridad_selected,
        "linkedin": linkedin_selected
    }
            
        
def validate_form_info(form_info):
    # Check required text fields
    if not form_info["actividad_formativa"] or not form_info["objetivo_desempeno"] or not form_info["contenidos"] or not form_info["skills"] or not form_info["keywords"]:
        return False

    # Check required dropdown fields (must not be None)
    required_dropdowns = ["gerencia", "desafio", "audiencia", "modalidad", "fuente", "prioridad"]
    for field in required_dropdowns:
        if form_info.get(field) is None:
            return False

    # Subgerencia and area are optional (can be None)
    return True


def get_id_from_name(lookup_dict, name):
    """Convert name to ID using lookup dictionary"""
    if name in lookup_dict:
        return lookup_dict[name]
    return None


def has_data_changed(original_row, new_form_data):
    """Compare original row data with new form data to detect changes"""
    # Define the mapping between form fields and database columns
    field_mapping = {
        'gerencia': 'Gerencia',
        'subgerencia': 'Subgerencia',
        'area': 'Área',
        'desafio': 'Desafío Estratégico',
        'actividad_formativa': 'Actividad Formativa',
        'objetivo_desempeno': 'Objetivo Desempeño',
        'contenidos': 'Contenidos',
        'skills': 'Skills',
        'keywords': 'Keywords',
        'audiencia': 'Audiencia',
        'modalidad': 'Modalidad',
        'fuente': 'Fuente',
        'fuente_interna': 'Fuente Interna',
        'prioridad': 'Prioridad',
        'linkedin': 'Curso Sugerido LinkedIn'
    }

    # Check each field for changes
    for form_field, db_column in field_mapping.items():
        original_value = str(original_row.get(db_column, "")).strip()
        new_value = str(new_form_data.get(form_field, "")).strip()

        if original_value != new_value:
            return True

    return False