import streamlit as st
import sqlite3
import pandas as pd
import os

# Check if the DB exists
if not os.path.exists("database.db"):
    # If not, run init_db.py to create it
    exec(open("init_db.py").read())

# Make page use full width
st.set_page_config(layout="wide")

conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

st.title("Plan de Formación")

# Load data
df = pd.read_sql_query("""
SELECT 
    gerencia AS Gerencia, 
    subgerencia AS Subgerencia,
    area AS Área, 
    desafio_estrategico AS Desafío_Estratégico, 
    actividad_formativa AS Actividad_Formativa, 
    objetivo_desempeno AS Objetivo_Desempeño, 
    contenidos_especificos AS Contenidos, 
    skills AS Skills, 
    keywords AS Keywords,
    modalidad_sugerida AS Modalidad, 
    audiencia AS Audiencia, 
    prioridad AS Prioridad, 
    created_at AS Fecha_Creación
FROM final_plan
ORDER BY gerencia
""", conn)

# Display only if there is data
if not df.empty:
    # Load data
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Plan no disponible. Por favor, completa el cuestionario DNC para generar un plan de formación.")