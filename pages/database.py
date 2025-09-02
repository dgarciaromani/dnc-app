import streamlit as st
import sqlite3
import pandas as pd
import time

# Make page use full width
st.set_page_config(layout="wide")

# Connect to DB
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

st.title("SQLite Data")

# Instructions box
st.markdown("""
### De uso interno, para revisar el contenido de las tablas de la base de datos.
""")

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]

if tables:
    selected_table = st.selectbox("Seleccionar tabla", tables)
    df = pd.read_sql_query(f"SELECT * FROM {selected_table}", conn)
    st.dataframe(df)
else:
    st.warning("No hay tablas en la base de datos.")

# Button to clear DB
with st.expander("Limpiar base de datos"):
    st.warning("Esta acción eliminará todos los datos de la base de datos. La información no se podrá recuperar una vez realizada esta acción.")
    confirm = st.checkbox("Quiero borrar todos los datos")
    if st.button("Borrar todo") and confirm:
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}';") # reset autoincrement
        conn.commit()
        st.success("Base de datos reiniciada.")
        st.session_state.clear()
        time.sleep(3)
        st.rerun()

conn.close()