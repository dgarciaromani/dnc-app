import streamlit as st
import sqlite3
import pandas as pd

# Make page use full width
st.set_page_config(layout="wide")

conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

st.title("Encuestados")

# Load data
df = pd.read_sql_query("""
SELECT 
    r.id AS ID,
    r.nombre AS Nombre,
    r.email AS Correo,
    r.nivel1 AS Gerencia,
    r.nivel2 AS Subgerencia,
    r.nivel3 AS Área,
    r.created_at AS Fecha_Creación,
    COUNT(d.submission_id) AS N_Necesidades
FROM respondents r
    JOIN raw_data_forms d ON r.id = d.submission_id
GROUP BY d.submission_id
""", conn)

# Display only if there is data
if not df.empty:
    # Load data
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Nadie ha contestado el cuestionario todavía.")