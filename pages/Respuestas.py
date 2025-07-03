import streamlit as st
import sqlite3
import pandas as pd

# Make page use full width
st.set_page_config(layout="wide")

conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

st.title("Respuestas del Cuestionario (datos no procesados)")

# Load data
df = pd.read_sql_query("""
SELECT 
    r.nombre AS Levantado_por,
    d.desafio AS Desafío_Estratégico,
    d.cambios AS Qué_Debe_Ocurrir,
    d.que_falta AS Qué_Falta,
    d.aprendizajes as Aprendizajes,
    d.audiencia AS Audiencia,
    d.fuente AS Fuente,
    d.prioridad AS Prioridad,         
    d.created_at AS Fecha_Creación
FROM respondents r
    JOIN raw_data_forms d ON r.id = d.submission_id
ORDER BY r.created_at DESC
""", conn)

# Display only if there is data
if not df.empty:
    # Load data
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Nadie ha contestado el cuestionario todavía.")