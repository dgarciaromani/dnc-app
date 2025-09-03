import streamlit as st
from src.data.database_utils import fetch_all

# Lookup values
gerencias_dict = fetch_all("gerencias")
subgerencias_dict = fetch_all("subgerencias")
areas_dict = fetch_all("areas")
desafios_dict = fetch_all("desafios")
audiencias_dict = fetch_all("audiencias")
modalidades_dict = fetch_all("modalidades")
fuentes_dict = fetch_all("fuentes")
prioridades_dict = fetch_all("prioridades")


def get_identification_data():

    # Instructions box
    st.markdown("""
    ## Instrucciones
    Por favor, completa el cuestionario para ayudarnos a identificar las necesidades de formación en tu área. 
    Primero completa tu información básica, luego añade hasta 5 necesidades y asigna una prioridad a cada una de ellas.
    """)

    # Basic information form
    with st.form("personal_info_form"):
        name = st.text_input("Nombre y Apellido", value=st.session_state.basic_info["name"])
        email = st.text_input("Correo Electrónico", value=st.session_state.basic_info["email"])
        
        # Gerencia selectbox
        gerencia_options = [(None, "Selecciona una Gerencia...")] + [(id, name) for name, id in gerencias_dict.items()]
        gerencia_selected, _ = st.selectbox(
            "Gerencia",
            options=gerencia_options,
            index=next(
                (i for i, g in enumerate(gerencia_options) if g[0] == st.session_state.basic_info["gerencia"]), 
                0
            ),
            format_func=lambda x: x[1]
        )

        # Subgerencia selectbox 
        subgerencia_options = [(None, "Selecciona una Subgerencia..."), (None, "N/A")] + [
            (id, name) for name, id in subgerencias_dict.items()
        ]
        subgerencia_selected, _ = st.selectbox(
            "Subgerencia",
            options=subgerencia_options,
            index=next(
                (i for i, g in enumerate(subgerencia_options) if g[0] == st.session_state.basic_info["subgerencia"]), 
                0
            ),
            format_func=lambda x: x[1]
        )

        # Área selectbox
        area_options = [(None, "Selecciona un Área..."), (None, "N/A")] + [
            (id, name) for name, id in areas_dict.items()
        ]
        area_selected, _ = st.selectbox(
            "Área",
            options=area_options,
            index=next(
                (i for i, g in enumerate(area_options) if g[0] == st.session_state.basic_info["area"]), 
                0
            ),
            format_func=lambda x: x[1]
        )

        submitted_basic = st.form_submit_button("Guardar datos")

    return submitted_basic, {
        "name": name,
        "email": email,
        "gerencia": gerencia_selected,
        "subgerencia": subgerencia_selected,
        "area": area_selected
    }


def get_form_data():
    
    with st.form("add_need_form", clear_on_submit=True):
        st.markdown("""
        Si no sabes cómo responder alguna pregunta, revisa el signo de pregunta (?) al lado derecho de cada campo para ver un ejemplo.
        """)
        challenge, _ = st.selectbox(
            "Desafío estratégico", 
            [(None, "Selecciona un desafío...")] + [(id, name) for name, id in desafios_dict.items()],
            index=0,
            format_func=lambda x: x[1]
        )
        changes = st.text_area(
            "¿Qué cosas deben ocurrir en tu gerencia/subgerencia/área/equipo para que se pueda cumplir este desafío o para mover sus indicadores?",
            label_visibility="visible",
            help="Ejemplo: Para cumplir con este desafío, se deben realizar informes de calidad y auto explicativos, que ayuden a comprender bien los procesos y reducir los tiempos de análisis",
        )
        whats_missing = st.text_area(
            "¿Qué le falta a tu equipo en términos de competencias, conocimientos y/o habilidades para cumplir este desafío? ¿Qué cosas no se hacen tan bien o podrían hacer mejor?",
            label_visibility="visible",
            help="Ejemplo: Los informes que se hacen en el área dejan mucho que desear porque uno los lee y no se entienden, además, vienen generalmente con errores",
        )
        learnings = st.text_area(
            "¿Cómo la capacitación podría ayudar al cumplimiento de desafío mencionado? ¿Qué debe aprender el equipo o persona(s)?",
            label_visibility="visible",
            help="Ejemplo: Serviría que manejen Excel en un nivel avanzado",
        )
        audience, _ = st.selectbox(
            "¿A quién debe ir dirigida la actividad formativa?",
            [(None, "Selecciona una audiencia...")] + [(id, name) for name, id in audiencias_dict.items()],
            index=0, 
            format_func=lambda x: x[1]
        )
        mode, _ = st.selectbox(
            "¿Qué modalidad debe tener la actividad formativa?",
            [(None, "Selecciona una modalidad...")] + [(id, name) for name, id in modalidades_dict.items()],
            index=0,
            format_func=lambda x: x[1]
        )
        source, _ = st.selectbox(
            "De acuerdo a lo que comentaste que el equipo debe aprender, ¿es un conocimiento que está dentro de la organización o debe ser impartido por una persona externa a la compañía?",
            [(None, "Selecciona una fuente...")] + [(id, name) for name, id in fuentes_dict.items()],
            index=0,
            format_func=lambda x: x[1]
        )
        internal_source = st.text_input(
            "Si el conocimiento está dentro de la organización, ¿quién(es) o dónde está? (de no ser interno, dejar en blanco)", 
            label_visibility="visible",
            help="Ejemplo: Eduardo Soto, de contabilidad; en el material del curso de certificación que realizamos el año pasado, o en el procedimiento 10.005",
            key="internal_source"
        )
        priority, _ = st.selectbox(
            "Prioriza estas en función de la urgencia/importancia para el logro de los desafíos y/o posibilidad de la ejecución de la actividad formativa según los tiempos del equipo",
            [(None, "Selecciona una prioridad...")] + [(id, name) for name, id in prioridades_dict.items()],
            index=0,
            format_func=lambda x: x[1]
        )
        
        add_clicked = st.form_submit_button(
            "Guardar necesidad"
            #disabled=(not challenge or not changes or not whats_missing or not learnings or not audience or not mode or not source or not priority)
        )

    return add_clicked, {
        "challenge": challenge,
        "changes": changes,
        "whats_missing": whats_missing,
        "learnings": learnings,
        "audience": audience,
        "mode": mode,
        "source": source,
        "internal_source": internal_source,
        "priority": priority
    }