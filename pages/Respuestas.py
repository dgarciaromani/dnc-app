import streamlit as st
import pandas as pd
from utils.database_utils import get_raw_data_forms

# Authentication check
if not st.session_state.get("authenticated", False):
    st.error("❌ Acceso no autorizado. Por favor, inicie sesión.")
    st.stop()

# Make page use full width
st.set_page_config(layout="wide")
st.title("Respuestas del Cuestionario (datos no procesados)")

# Load data
data = get_raw_data_forms()
df = pd.DataFrame(data)

# Display only if there is data
if not df.empty:
    # Load data
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Nadie ha contestado el cuestionario todavía.")