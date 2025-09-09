import streamlit as st
import pandas as pd
from src.data.database_utils import get_respondents

# Authentication check
if not st.session_state.get("authenticated", False):
    st.error("❌ Acceso no autorizado. Por favor, inicie sesión.")
    st.stop()

# Make page use full width
st.set_page_config(layout="wide")
st.title("Encuestados")

# Load data
respondents = get_respondents()
df = pd.DataFrame(respondents)

# Display only if there is data
if not df.empty:
    # Load data
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Nadie ha contestado el cuestionario todavía.")
