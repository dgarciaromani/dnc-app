import streamlit as st
import pandas as pd
from src.data.database_utils import fetch_plan

def show_filters(df):
    # Create filter columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Gerencia filter
        gerencias = sorted(df["Gerencia"].dropna().unique())
        selected_gerencias = st.multiselect(
            "Gerencia",
            options=gerencias,
            default=st.session_state.filters.get("Gerencia", []),
            placeholder="Elige una Gerencia",
            key="gerencia_filter"
        )
        st.session_state.filters["Gerencia"] = selected_gerencias

        # Audiencia filter
        audiencias = sorted(df["Audiencia"].dropna().unique())
        selected_audiencias = st.multiselect(
            "Audiencia",
            options=audiencias,
            default=st.session_state.filters.get("Audiencia", []),
            placeholder="Elige una Audiencia",
            key="audiencia_filter"
        )
        st.session_state.filters["Audiencia"] = selected_audiencias

        # Asociaciones filter
        asociaciones = ["Con cursos asociados", "Sin cursos asociados"]
        selected_asociaciones = st.multiselect(
            "Asociaciones",
            options=asociaciones,
            default=st.session_state.filters.get("Asociaciones", []),
            placeholder="Elige un Estado",
            key="asociacion_filter"
        )
        st.session_state.filters["Asociaciones"] = selected_asociaciones

    with col2:
        # Subgerencia filter
        subgerencias = sorted(df["Subgerencia"].dropna().unique())
        selected_subgerencias = st.multiselect(
            "Subgerencia",
            options=subgerencias,
            default=st.session_state.filters.get("Subgerencia", []),
            placeholder="Elige una Subgerencia",
            key="subgerencia_filter"
        )
        st.session_state.filters["Subgerencia"] = selected_subgerencias

        # Modalidad filter
        modalidades = sorted(df["Modalidad"].dropna().unique())
        selected_modalidades = st.multiselect(
            "Modalidad",
            options=modalidades,
            default=st.session_state.filters.get("Modalidad", []),
            placeholder="Elige una Modalidad",
            key="modalidad_filter"
        )
        st.session_state.filters["Modalidad"] = selected_modalidades            

    with col3:
        # Área filter
        areas = sorted(df["Área"].dropna().unique())
        selected_areas = st.multiselect(
            "Área",
            options=areas,
            default=st.session_state.filters.get("Área", []),
            placeholder="Elige un Área",
            key="area_filter"
        )
        st.session_state.filters["Área"] = selected_areas

        # Fuente filter
        fuentes = sorted(df["Fuente"].dropna().unique())
        selected_fuentes = st.multiselect(
            "Fuente",
            options=fuentes,
            default=st.session_state.filters.get("Fuente", []),
            placeholder="Elige una Fuente",
            key="fuente_filter"
        )
        st.session_state.filters["Fuente"] = selected_fuentes            

    with col4:
        # Desafío Estratégico filter
        desafios = sorted(df["Desafío Estratégico"].dropna().unique())
        selected_desafios = st.multiselect(
            "Desafío Estratégico",
            options=desafios,
            default=st.session_state.filters.get("Desafío Estratégico", []),
            placeholder="Elige un Desafío Estratégico",
            key="desafio_filter"
        )
        st.session_state.filters["Desafío Estratégico"] = selected_desafios

        # Prioridad filter
        prioridades = sorted(df["Prioridad"].dropna().unique())
        selected_prioridades = st.multiselect(
            "Prioridad",
            options=prioridades,
            default=st.session_state.filters.get("Prioridad", []),
            placeholder="Elige una Prioridad",
            key="prioridad_filter"
        )
        st.session_state.filters["Prioridad"] = selected_prioridades

    # Clear filters button
    col_clear, col_space = st.columns([1, 3])
    with col_clear:
        if st.button("🗑️ Limpiar Filtros", type="primary"):
            st.session_state.filters = {}
            st.rerun()


def reload_data():
    """
    Reload the plan data from database and return as DataFrame
    Returns: pandas.DataFrame - Fresh data from the database
    """
    data = fetch_plan()
    df = pd.DataFrame(data)
    # Ensure the dataframe has a proper integer index starting from 0
    df.reset_index(drop=True, inplace=True)
    return df