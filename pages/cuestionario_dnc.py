import streamlit as st
import pandas as pd
import json
from src.forms.dnc_form import get_identification_data, get_form_data
from src.data.database_utils import fetch_all, update_respondents, update_raw_data_forms, insert_row_into_plan
from src.services.bedrock_api import get_from_ai, process_response
from src.auth.authentication import stay_authenticated

# Authentication check
if not st.session_state.get("authenticated", False):
    st.error("❌ Acceso no autorizado. Por favor, inicie sesión.")
    st.stop()

# Global variables
MAXNEEDS = 5
desafios_dict = fetch_all("desafios")
audiencias_dict = fetch_all("audiencias")
modalidades_dict = fetch_all("modalidades")
fuentes_dict = fetch_all("fuentes")
prioridades_dict = fetch_all("prioridades")

# Make page use full width & set title
st.set_page_config(layout="wide")
st.title("Cuestionario DNC")

# Initialize session state
if "basic_info_saved" not in st.session_state:
    st.session_state.basic_info_saved = False

if "basic_info" not in st.session_state:
    st.session_state.basic_info = {
        "name": "",
        "email": "",
        "gerencia": None,
        "subgerencia": None,
        "area": None
    }

if "needs_count" not in st.session_state:
    st.session_state.needs_count = 0

if "needs_list" not in st.session_state:
    st.session_state.needs_list = []

if "submission_id" not in st.session_state:
    st.session_state.submission_id = None

# Step 1: Initial form to collect user information
if not st.session_state.basic_info_saved:
    submitted_basic, basic_info = get_identification_data()

    # Submit basic info form
    if submitted_basic:
        if not basic_info["name"].strip() or not basic_info["email"].strip() or basic_info["gerencia"] is None:
            st.error("Por favor completa todos los campos.")
        else:
            st.session_state.basic_info.update({
                "name": basic_info["name"].strip(),
                "email": basic_info["email"].strip(),
                "gerencia": basic_info["gerencia"],
                "subgerencia": basic_info["subgerencia"],
                "area": basic_info["area"],
            })
            st.session_state.basic_info_saved = True
            st.success("Datos guardados correctamente.")
            st.rerun()

# Step 2: Needs form
else:
    # New user button - only show for admin users
    user_role = st.session_state.get("role", "user")
    if user_role == "admin":
        with st.expander(f"Guardando información como {st.session_state.basic_info['name']}. Para un nuevo usuario, haz clic aquí"):
            if st.button("👤 Nuevo usuario/formulario", type="primary"):
                user_data = {
                    "name": st.session_state.name,
                    "role": st.session_state.role,
                    "username": st.session_state.username
                }
                st.session_state.clear()
                stay_authenticated(user_data["name"], user_data["role"], user_data["username"])
                st.rerun()

    # Display needs list if it exists
    if len(st.session_state.needs_list) > 0:
        st.subheader(f"Necesidades registradas por {st.session_state.basic_info['name']}:")
        for i, need in enumerate(st.session_state.needs_list):
            st.markdown(f"{i+1}. Desafío: {need['challenge']}, ¿Qué le falta a tu equipo para cumplir este desafío?: {need['whats_missing']}")

    # Display needs form
    st.subheader("🎯 Tus desafíos estratégicos:")
    st.markdown("\n".join([f"{i+1}. {d}" for i, d in enumerate(desafios_dict.keys())]))

    # Check if the user has reached the maximum number of needs   
    if st.session_state.needs_count < MAXNEEDS:
        add_clicked, form_info = get_form_data()

        # Submit form
        if add_clicked:
            if form_info["challenge"] is None or not form_info["changes"].strip() or not form_info["whats_missing"].strip() or not form_info["learnings"] or form_info["audience"] is None or form_info["mode"] is None or not form_info["source"] or form_info["priority"] is None:
                st.error("Por favor completa todos los campos con (*).")
            else:
                with st.spinner("Procesando y guardando la información para el Plan... Por favor espera ⏳"):
                    # Insert user information into the database
                    if st.session_state.submission_id is None:
                        submission_id = update_respondents(
                            st.session_state.basic_info["name"], 
                            st.session_state.basic_info["email"]
                        )
                        st.session_state.submission_id = submission_id

                    update_raw_data_forms(
                        st.session_state.submission_id,
                        "DNC",
                        st.session_state.basic_info["gerencia"],
                        st.session_state.basic_info["subgerencia"],
                        st.session_state.basic_info["area"],
                        form_info["challenge"],
                        form_info["changes"],
                        form_info["whats_missing"],
                        form_info["learnings"],
                        form_info["audience"],
                        form_info["mode"],
                        form_info["source"],
                        form_info["internal_source"],
                        form_info["priority"]
                    )

                    # Append to list in session state and update count
                    challenge_name = next(name for name, id in desafios_dict.items() if id == form_info["challenge"])
                    audience_name = next(name for name, id in audiencias_dict.items() if id == form_info["audience"])
                    modality_name = next(name for name, id in modalidades_dict.items() if id == form_info["mode"])
                    priority_name = next(name for name, id in prioridades_dict.items() if id == form_info["priority"])

                    st.session_state.needs_count += 1
                    st.session_state.needs_list.append(
                        {"challenge": challenge_name,
                         "whats_missing": form_info["whats_missing"].strip()}
                    )

                    # Run script to call Bedrock's API
                    # Prepare need data for API call
                    need_list = []
                    need_list.append({
                        "desafio": challenge_name,
                        "cambios": form_info["changes"],
                        "que_falta": form_info["whats_missing"],
                        "aprendizajes": form_info["learnings"],
                        "audiencia": audience_name,
                        "modalidad": modality_name,
                        "prioridad": priority_name
                    })
                    need_json = json.dumps(need_list, ensure_ascii=False, indent=2)
                    contents = [need_json]
                    prompt = st.secrets["prompt_add"]

                    # Call AI API
                    response = get_from_ai(prompt, contents)

                    # Process the response
                    processed_response = process_response(response)

                    for item in processed_response:
                        insert_row_into_plan(
                            item, 
                            "DNC",
                            st.session_state.basic_info["gerencia"],
                            st.session_state.basic_info["subgerencia"],
                            st.session_state.basic_info["area"],
                            form_info["challenge"],
                            form_info["mode"],
                            form_info["audience"],
                            form_info["source"],
                            form_info["internal_source"],
                            form_info["priority"]
                        )

                    st.rerun()

    # Confirmation message
    if st.session_state.submission_id != None:
        st.success("La necesidad se ha guardado correctamente.")
    
    # Max needs warning
    if st.session_state.needs_count >= MAXNEEDS:
        st.warning(f"Has alcanzado el máximo de {MAXNEEDS} necesidades.")
