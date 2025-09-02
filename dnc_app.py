import streamlit as st
import os
from utils.database_utils import fill_database_from_template

# Check if the DB exists
if not os.path.exists("database.db"):
    # If not, run init_db.py to create it
    exec(open("init_db.py").read())

# Fill the database with initial data 
fill_database_from_template()

# Define pages
dashboard = st.Page("pages/dashboard.py", title="Dashboard", icon=":material/dashboard:")
plans = st.Page("pages/plan_formacion.py", title="Mi Plan de Formación", icon=":material/list:")
dnc = st.Page("pages/cuestionario_DNC.py", title="Cuestionario DNC", icon=":material/question_answer:")
search_course = st.Page("pages/buscar_cursos.py", title="Buscar y Agregar Cursos", icon=":material/search:")
respondents = st.Page("pages/encuestados.py", title="Encuestados", icon=":material/group:")
responses = st.Page("pages/respuestas.py", title="Respuestas", icon=":material/feedback:")
desplegables = st.Page("pages/desplegables.py", title="Administrar desplegables", icon=":material/arrow_drop_down_circle:")
linkedin_courses = st.Page("pages/cursos_linkedin.py", title="Cursos LinkedIn", icon=":material/school:")
database = st.Page("pages/database.py", title="Base de Datos", icon=":material/database:")

# Group pages under categories
nav = st.navigation({
    "Home:": [dashboard],
    "Plan de Formación:": [plans],
    "Agregar necesidades:": [dnc],
    "Cursos en LinkedIn:": [linkedin_courses, search_course],
    "Administración:": [respondents, responses, desplegables, database],
})

# Run navigation
nav.run()