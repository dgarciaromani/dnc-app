import streamlit as st


def show_validation_filters(df, tab_prefix="", session_state_key="validation_filters"):
    """Show filters with unique keys for validation page"""
    # Create filter columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Gerencia filter
        if "Gerencia" in df.columns:
            gerencias = sorted(df["Gerencia"].dropna().unique())
            selected_gerencias = st.multiselect(
                "Gerencia",
                options=gerencias,
                default=st.session_state[session_state_key].get("Gerencia", []),
                placeholder="Elige una Gerencia",
                key=f"{tab_prefix}_validation_gerencia_filter"
            )
            st.session_state[session_state_key]["Gerencia"] = selected_gerencias

        # Audiencia filter
        if "Audiencia" in df.columns:
            audiencias = sorted(df["Audiencia"].dropna().unique())
            selected_audiencias = st.multiselect(
                "Audiencia",
                options=audiencias,
                default=st.session_state[session_state_key].get("Audiencia", []),
                placeholder="Elige una Audiencia",
                key=f"{tab_prefix}_validation_audiencia_filter"
            )
            st.session_state[session_state_key]["Audiencia"] = selected_audiencias

        # Asociaciones filter
        asociaciones = ["Con cursos asociados", "Sin cursos asociados"]
        selected_asociaciones = st.multiselect(
            "Asociaciones",
            options=asociaciones,
            default=st.session_state[session_state_key].get("Asociaciones", []),
            placeholder="Elige un Estado",
            key=f"{tab_prefix}_validation_asociacion_filter"
        )
        st.session_state[session_state_key]["Asociaciones"] = selected_asociaciones

    with col2:
        # Subgerencia filter
        if "Subgerencia" in df.columns:
            subgerencias = sorted(df["Subgerencia"].dropna().unique())
            selected_subgerencias = st.multiselect(
                "Subgerencia",
                options=subgerencias,
                default=st.session_state[session_state_key].get("Subgerencia", []),
                placeholder="Elige una Subgerencia",
                key=f"{tab_prefix}_validation_subgerencia_filter"
            )
            st.session_state[session_state_key]["Subgerencia"] = selected_subgerencias

        # Modalidad filter
        if "Modalidad" in df.columns:
            modalidades = sorted(df["Modalidad"].dropna().unique())
            selected_modalidades = st.multiselect(
                "Modalidad",
                options=modalidades,
                default=st.session_state[session_state_key].get("Modalidad", []),
                placeholder="Elige una Modalidad",
                key=f"{tab_prefix}_validation_modalidad_filter"
            )
            st.session_state[session_state_key]["Modalidad"] = selected_modalidades

    with col3:
        # Área filter
        if "Área" in df.columns:
            areas = sorted(df["Área"].dropna().unique())
            selected_areas = st.multiselect(
                "Área",
                options=areas,
                default=st.session_state[session_state_key].get("Área", []),
                placeholder="Elige un Área",
                key=f"{tab_prefix}_validation_area_filter"
            )
            st.session_state[session_state_key]["Área"] = selected_areas

        # Fuente filter
        if "Fuente" in df.columns:
            fuentes = sorted(df["Fuente"].dropna().unique())
            selected_fuentes = st.multiselect(
                "Fuente",
                options=fuentes,
                default=st.session_state[session_state_key].get("Fuente", []),
                placeholder="Elige una Fuente",
                key=f"{tab_prefix}_validation_fuente_filter"
            )
            st.session_state[session_state_key]["Fuente"] = selected_fuentes

    with col4:
        # Desafío Estratégico filter
        if "Desafío Estratégico" in df.columns:
            desafios = sorted(df["Desafío Estratégico"].dropna().unique())
            selected_desafios = st.multiselect(
                "Desafío Estratégico",
                options=desafios,
                default=st.session_state[session_state_key].get("Desafío Estratégico", []),
                placeholder="Elige un Desafío Estratégico",
                key=f"{tab_prefix}_validation_desafio_filter"
            )
            st.session_state[session_state_key]["Desafío Estratégico"] = selected_desafios

        # Prioridad filter
        if "Prioridad" in df.columns:
            prioridades = sorted(df["Prioridad"].dropna().unique())
            selected_prioridades = st.multiselect(
                "Prioridad",
                options=prioridades,
                default=st.session_state[session_state_key].get("Prioridad", []),
                placeholder="Elige una Prioridad",
                key=f"{tab_prefix}_validation_prioridad_filter"
            )
            st.session_state[session_state_key]["Prioridad"] = selected_prioridades

    # Clear filters button
    col_clear, col_space = st.columns([1, 3])
    with col_clear:
        if st.button("🗑️ Limpiar Filtros", type="primary", key=f"{tab_prefix}_validation_clear_filters"):
            st.session_state[session_state_key] = {}
            st.rerun()