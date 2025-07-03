import streamlit as st
import sqlite3
import requests
import re
import json
from datetime import datetime
from selectbox_options import GERENCIAS, SUBGERENCIAS, AREAS, DESAFIOS, MAXNEEDS, AUDIENCIAS, PRIORIDAD, MODALIDADES

# Make page use full width
st.set_page_config(layout="wide")

# Connect to database
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

# Page's title
st.title("Cuestionario DNC")

# Initialize session state
if "basic_info_saved" not in st.session_state:
    st.session_state.basic_info_saved = False

if "basic_info" not in st.session_state:
    st.session_state.basic_info = {}

if "needs_count" not in st.session_state:
    st.session_state.needs_count = 0

if "needs_list" not in st.session_state:
    st.session_state.needs_list = []

if "submission_id" not in st.session_state:
    st.session_state.submission_id = None

# Step 1: Initial form to collect user information
if not st.session_state.basic_info_saved:
    
    # Instructions box
    st.markdown("""
    ## Instrucciones
    Por favor, completa el cuestionario para ayudarnos a identificar las necesidades de formación en tu área. 
    Primero completa tu información básica, luego añade hasta 5 necesidades y asigna una prioridad a cada una de ellas.
    """)

    # Basic information form
    with st.form("personal_info_form"):
        name = st.text_input("Nombre y Apellido")
        email = st.text_input("Correo Electrónico")
        level1 = st.selectbox("Gerencia", ["Selecciona una Gerencia..."] + GERENCIAS)
        level2 = st.selectbox("Subgerencia", ["Selecciona una Subgerencia..."] + SUBGERENCIAS)
        level3 = st.selectbox("Área", ["Selecciona un Área..."] + AREAS)
        submitted_basic = st.form_submit_button("Guardar datos")

    # Submit basic info form
    if submitted_basic:
        if not name.strip() or not email.strip() or level1 == "Selecciona una Gerencia..." or level2 == "Selecciona una Subgerencia..." or level3 == "Selecciona un Área...":
            st.error("Por favor completa todos los campos.")
        else:
            # Store data in session state only
            st.session_state.basic_info = {
                "name": name.strip(), 
                "email": email.strip(), 
                "level1": level1, 
                "level2": level2, 
                "level3": level3
                }
            st.session_state.basic_info_saved = True
            st.success("Datos guardados correctamente.")
            st.rerun()

# Step 2: Needs form
else: 
    # New user button
    if st.button("Nuevo usuario/formulario"):
        st.session_state.clear()
        st.rerun()
    
    # Confirmation message
    if st.session_state.submission_id != None:
        st.success("La necesidad se ha guardado correctamente.")

    # Display needs list if it exists
    if len(st.session_state.needs_list)> 0:
        st.subheader("Tus necesidades registradas:")
        for i, need in enumerate(st.session_state.needs_list):
            st.markdown(f"{i+1}. Desafío: {need['challenge']}, ¿Qué le falta a tu equipo para cumplir este desafío?: {need['whats_missing']}")

    # Display needs form
    st.subheader("Tus desafíos estratégicos:")
    st.markdown("\n".join([f"{i+1}. {d}" for i, d in enumerate(DESAFIOS)]))

    # Check if the user has reached the maximum number of needs   
    if st.session_state.needs_count < MAXNEEDS:
        with st.form("add_need_form", clear_on_submit=True):
            # Instructions box
            st.markdown("""
            ##### Si no sabes cómo responder alguna pregunta, revisa el signo de pregunta (?) al lado derecho de cada campo para ver un ejemplo.
            """)
            challenge = st.selectbox(
                "Desafío estratégico", 
                ["Selecciona un desafío..."] + DESAFIOS,
                index=0,
                key="challenge_input")
            changes = st.text_area(
                "¿Qué cosas deben ocurrir en tu subgerencia/área/equipo para que se pueda cumplir este desafío o para mover sus indicadores?",
                label_visibility="visible",
                help="Ejemplo: Para cumplir con este desafío, se deben realizar informes de calidad y auto explicativos, que ayuden a comprender bien los procesos y reducir los tiempos de análisis",
                key="changes_input")
            whats_missing = st.text_area(
                "¿Qué le falta a tu equipo en términos de competencias, conocimientos y/o habilidades para cumplir este desafío? ¿Qué cosas no se hacen tan bien o podrían hacer mejor?",
                label_visibility="visible",
                help="Ejemplo: Los informes que se hacen en el área dejan mucho que desear porque uno los lee y no se entienden, además, vienen generalmente con errores",
                key="whats_missing_input")
            learnings = st.text_area(
                "¿Cómo la capacitación podría ayudar al cumplimiento de desafío mencionado? ¿Qué debe aprender el equipo o persona(s)?",
                label_visibility="visible",
                help="Ejemplo: Serviría que manejen Excel en un nivel avanzado",
                key="learnings_input")
            audience = st.selectbox(
                "¿A quién debe ir dirigida la actividad formativa? Puede ser un rol o cargo, una persona, algunos miembros del equipo o el equipo completo",
                ["Selecciona una audiencia..."] + AUDIENCIAS,
                index=0, 
                key="audience_input")
            source = st.text_input(
                "De acuerdo a lo que comentaste que el equipo (o persona) debe aprender, ¿es un conocimiento que está dentro de la organización o debe ser impartido por una persona externa a la compañía? Considerando si el conocimiento está dentro de la organización, ¿quién(es) o dónde está?", 
                label_visibility="visible",
                help="Ejemplo: Eduardo Soto, de contabilidad; en el material del curso de certificación que realizamos el año pasado, o en el procedimiento 10.005",
                key="source_input")
            priority = st.selectbox(
                "Prioriza estas en función de la urgencia/importancia para el logro de los desafíos y/o posibilidad de la ejecución de la actividad formativa según los tiempos del equipo",
                ["Selecciona una prioridad..."] + PRIORIDAD,
                index=0,
                key="priority_input")
            add_clicked = st.form_submit_button("Guardar necesidad")

        # Submit form
        if add_clicked:
            if  challenge == "Selecciona un desafío..." or not changes.strip() or not whats_missing.strip() or not learnings or audience == "Selecciona una audiencia..." or not source or priority == "Selecciona una prioridad...":
                st.error("Por favor completa todos los campos.")
            else:
                # Insert user information into the database
                if st.session_state.submission_id is None:
                    c.execute(
                        "INSERT INTO respondents (nombre, email, nivel1, nivel2, nivel3) VALUES (?, ?, ?, ?, ?)",
                        (
                            st.session_state.basic_info["name"], 
                            st.session_state.basic_info["email"], 
                            st.session_state.basic_info["level1"], 
                            st.session_state.basic_info["level2"], 
                            st.session_state.basic_info["level3"]
                        )
                    )
                    conn.commit()
                    st.session_state.submission_id = c.lastrowid

                # Insert need into the database
                c.execute(
                    """
                    INSERT INTO raw_data_forms (submission_id, desafio, cambios, que_falta, aprendizajes, audiencia, fuente, prioridad)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        st.session_state.submission_id,
                        challenge,
                        changes,
                        whats_missing,
                        learnings,
                        audience,
                        source,
                        priority
                    )
                )
                conn.commit()

                # Append to list in session state and update count
                st.session_state.needs_count += 1
                st.session_state.needs_list.append(
                    {"challenge": challenge, "whats_missing": whats_missing.strip()}
                )

                # Insert availability
                #############################
                #c.execute(
                #    """
                #    INSERT INTO availability (submission_id, audiencia, disponiblidad, no_disponible)
                #    VALUES (?, ?, ?, ?)
                #    """,
                #    (submission_id, audience, availability, not_available)
                #)
                ##############################

                # Run script to call Bedrock's API
                # Prepare need data for API call
                need_list = []
                need_list.append({
                    "gerencia": st.session_state.basic_info["level1"],
                    "subgerencia": st.session_state.basic_info["level2"],
                    "area": st.session_state.basic_info["level3"],
                    "desafio": challenge,
                    "cambios": changes,
                    "que_falta": whats_missing,
                    "aprendizajes": learnings,
                    "audiencia": audience,
                    "fuente": source,
                    "prioridad": priority                        
                })
                need_json = json.dumps(need_list, ensure_ascii=False, indent=2)

                # Prepare plan data for API call
                # Query full plan data
                c.execute(
                    """
                    SELECT 
                        gerencia,
                        subgerencia,
                        area,
                        desafio_estrategico,
                        actividad_formativa,
                        objetivo_desempeno,
                        contenidos_especificos,
                        skills,
                        modalidad_sugerida,
                        audiencia,
                        prioridad
                    FROM final_plan
                    """
                )
                rows = c.fetchall()
                plan_list = []
                for row in rows:
                    plan_list.append({
                        "gerencia": row[0],
                        "subgerencia": row[1],
                        "area": row[2],
                        "desafio_estrategico": row[3],
                        "actividad_formativa": row[4],
                        "objetivo_desempeno": row[5],
                        "contenidos_especificos": row[6],
                        "skills": row[7],
                        "modalidad_sugerida": row[8],
                        "audiencia": row[9],
                        "prioridad": row[10]
                    })
                plan_json = json.dumps(plan_list, ensure_ascii=False, indent=2)

                # Prepare API call
                url = st.secrets["url"]
                auth_token = st.secrets["auth_token"]
                prompt = st.secrets["prompt_add"]
                headers = {
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json",
                    "accept": "application/json"
                }

                payload = {
                    "model": "us.deepseek.r1-v1:0",  # Change if needed
                    "conversation": [
                        {
                            "content": [
                                {"text": prompt},
                                {"text": need_json},
                                {"text": plan_json}
                            ],
                            "role": "user"
                        }
                    ]
                }

                # Make the request
                response = requests.post(url, headers=headers, data=json.dumps(payload))

                print("Response status code:", response.status_code)  # Debugging

                # Convert raw response to a dict
                response_json = response.json()

                # Extract the "response" field from the API response
                markdown_response = response_json["response"]

                # Extract the JSON block from markdown using regex
                match = re.search(r'```json\n(.*?)\n```', markdown_response, re.DOTALL)
                json_str = match.group(1) if match else None

                 # Convert JSON string to Python list of dicts
                data = json.loads(json_str)

                for item in data:
                    c.execute(
                        """
                        INSERT INTO final_plan (
                            gerencia,
                            subgerencia,
                            area,
                            desafio_estrategico,
                            actividad_formativa,
                            objetivo_desempeno,
                            contenidos_especificos,
                            skills,
                            modalidad_sugerida,
                            audiencia,
                            prioridad
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            item.get("Gerencia"),
                            item.get("Subgerencia"),
                            item.get("Área"),
                            item.get("Desafío estratégico que apalanca"),
                            item.get("Actividad formativa"),
                            item.get("Objetivo de desempeño"),
                            item.get("Contenidos específicos"),
                            item.get("Skills"),
                            item.get("Modalidad sugerida"),
                            item.get("Audiencia"),
                            item.get("Prioridad")
                        )
                    )
                conn.commit()
                st.rerun()

    ## REVIEW THIS
    if st.session_state.needs_count >= MAXNEEDS:
        st.warning("Has alcanzado el máximo de {MAXNEEDS} necesidades.")

    # Final form to submit all data
    ######################################
    #st.subheader("Preguntas finales")
    #availability = st.text_input("¿Cuántas horas seguidas puede ausentarse este equipo o persona de su trabajo diario o semanal o mensual para capacitarse; en base a las posibilidades del equipo y las demandas al área? (no es lo que nos gustaría sino lo que se ve posible de participar)")
    #not_available = st.text_input("Cuándo NO es posible que el equipo o persona participe de una capacitación? Nombrar cuáles podrían ser buenas o malas fechas para capacitarse")
    ######################################

    ## TODO: Validate availability and not_available inputs

    #conn.close()