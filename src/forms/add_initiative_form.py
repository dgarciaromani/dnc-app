import streamlit as st
from src.data.database_utils import fetch_all, insert_row_into_plan

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


def add_initiative_form():
    """
    Display form for adding new training initiative
    Returns: (submitted, form_data) tuple
    """
    with st.form("add_initiative_form", clear_on_submit=True):

        # Gerencia dropdown
        gerencia_options = [None] + [name for name, id in gerencias.items()]
        gerencia_selected = st.selectbox(
            "Gerencia (*)",
            options=gerencia_options,
            index=0,
            format_func=lambda x: "Selecciona una Gerencia..." if x is None else x
        )

        # Subgerencia dropdown
        subgerencia_options = [None, "N/A"] + [name for name, id in subgerencias.items()]
        subgerencia_selected = st.selectbox(
            "Subgerencia",
            options=subgerencia_options,
            index=0,
            format_func=lambda x: "Selecciona una Subgerencia..." if x is None else x
        )

        # Área dropdown
        area_options = [None, "N/A"] + [name for name, id in areas.items()]
        area_selected = st.selectbox(
            "Área",
            options=area_options,
            index=0,
            format_func=lambda x: "Selecciona un Área..." if x is None else x
        )

        # Desafío Estratégico dropdown
        desafio_options = [None] + [name for name, id in desafios.items()]
        desafio_selected = st.selectbox(
            "Desafío Estratégico (*)",
            options=desafio_options,
            index=0,
            format_func=lambda x: "Selecciona un Desafío Estratégico..." if x is None else x
        )

        # Actividad formativa
        actividad_formativa = st.text_input(
            "Actividad Formativa (*)",
            value="",
            help="Describe la actividad formativa que se va a desarrollar"
        )

        # Objetivo Desempeño
        objetivo_desempeno = st.text_area(
            "Objetivo Desempeño (*)",
            value="",
            help="¿Qué cosas deben ocurrir para cumplir este desafío?",
            height=100
        )

        # Contenidos
        contenidos = st.text_area(
            "Contenidos (*)",
            value="",
            help="¿Qué le falta al equipo en términos de competencias?",
            height=100
        )

        # Skills
        skills = st.text_area(
            "Skills (*)",
            value="",
            help="Habilidades específicas que se deben desarrollar",
            height=80
        )

        # Keywords
        keywords = st.text_input(
            "Keywords (*)",
            value="",
            help="Palabras clave para búsqueda de cursos relacionados"
        )

        # Audiencia dropdown
        audiencia_options = [None] + [name for name, id in audiencias.items()]
        audiencia_selected = st.selectbox(
            "Audiencia (*)",
            options=audiencia_options,
            index=0,
            format_func=lambda x: "Selecciona una Audiencia..." if x is None else x
        )

        # Modalidad dropdown
        modalidad_options = [None] + [name for name, id in modalidades.items()]
        modalidad_selected = st.selectbox(
            "Modalidad (*)",
            options=modalidad_options,
            index=0,
            format_func=lambda x: "Selecciona una Modalidad..." if x is None else x
        )

        # Fuente dropdown
        fuente_options = [None] + [name for name, id in fuentes.items()]
        fuente_selected = st.selectbox(
            "Fuente (*)",
            options=fuente_options,
            index=0,
            format_func=lambda x: "Selecciona una Fuente..." if x is None else x
        )

        # Fuente Interna
        fuente_interna = st.text_input(
            "Fuente Interna",
            value="",
            help="¿Quién o dónde está el conocimiento internamente?"
        )

        # Prioridad dropdown
        prioridad_options = [None] + [name for name, id in prioridades.items()]
        prioridad_selected = st.selectbox(
            "Prioridad (*)",
            options=prioridad_options,
            index=0,
            format_func=lambda x: "Selecciona una Prioridad..." if x is None else x
        )

        # LinkedIn course dropdown (optional)
        linkedin_options = [None] + [name for name, id in linkedin.items()]
        linkedin_selected = st.selectbox(
            "Curso Sugerido LinkedIn",
            options=linkedin_options,
            index=0,
            format_func=lambda x: "Selecciona un curso (opcional)..." if x is None else x
        )

        # Submit button
        submitted = st.form_submit_button("Agregar Iniciativa", type="primary")

    # Prepare form data dictionary
    form_data = {
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

    return submitted, form_data


def validate_add_form_info(form_info):
    """
    Validate form data for adding new initiative
    Returns: Boolean indicating if form is valid
    """
    # Check required text fields
    required_text_fields = [
        "actividad_formativa",
        "objetivo_desempeno",
        "contenidos",
        "skills",
        "keywords"
    ]

    for field in required_text_fields:
        if not form_info.get(field) or not form_info.get(field).strip():
            return False

    # Check required dropdown fields (must not be None)
    required_dropdowns = ["gerencia", "desafio", "audiencia", "modalidad", "fuente", "prioridad"]
    for field in required_dropdowns:
        if form_info.get(field) is None:
            return False

    # Subgerencia and area are optional (can be None)
    return True


def get_id_from_name(lookup_dict, name):
    """
    Convert name to ID using lookup dictionary
    """
    if name in lookup_dict:
        return lookup_dict[name]
    return None


def save_new_initiative(form_data):
    """
    Save new initiative to database
    Returns: Boolean indicating success
    """
    try:
        # Convert names to IDs
        gerencia_id = get_id_from_name(gerencias, form_data['gerencia'])
        subgerencia_id = get_id_from_name(subgerencias, form_data['subgerencia']) if form_data['subgerencia'] and form_data['subgerencia'] != "N/A" else None
        area_id = get_id_from_name(areas, form_data['area']) if form_data['area'] and form_data['area'] != "N/A" else None
        desafio_id = get_id_from_name(desafios, form_data['desafio'])
        audiencia_id = get_id_from_name(audiencias, form_data['audiencia'])
        modalidad_id = get_id_from_name(modalidades, form_data['modalidad'])
        fuente_id = get_id_from_name(fuentes, form_data['fuente'])
        prioridad_id = get_id_from_name(prioridades, form_data['prioridad'])

        # Prepare data for insertion
        initiative_data = {
            "Actividad formativa": form_data['actividad_formativa'],
            "Objetivo de desempeño": form_data['objetivo_desempeno'],
            "Contenidos específicos": form_data['contenidos'],
            "Skills": form_data['skills'],
            "Keywords": form_data['keywords']
        }

        # Insert into database
        insert_row_into_plan(
            data=initiative_data,
            gerencia_id=gerencia_id,
            subgerencia_id=subgerencia_id,
            area_id=area_id,
            desafio_id=desafio_id,
            modalidad_id=modalidad_id,
            audiencia_id=audiencia_id,
            fuente_id=fuente_id,
            fuente_interna=form_data['fuente_interna'],
            prioridad_id=prioridad_id
        )

        return True

    except Exception as e:
        st.error(f"❌ Error al guardar la nueva iniciativa: {str(e)}")
        return False
