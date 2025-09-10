import streamlit as st

def show_course_filters(df):
    """Display filters for course search page (Estado, Gerencia, Audiencia, Prioridad)"""
    # Create filter columns
    col1, col2, col3, col4 = st.columns(4)

    # Initialize filters if not exists
    if "course_filters" not in st.session_state:
        st.session_state.course_filters = {}

    with col1:
        # Estado filter (Estado Curso) - binary filter: with/without courses
        if "Estado Curso" in df.columns:
            # Check if Estado Curso column has any non-empty values
            has_courses = df["Estado Curso"].notna() & (df["Estado Curso"] != "")
            has_any_courses = has_courses.any()

            if has_any_courses:
                estado_options = ["Con cursos asociados", "Sin cursos asociados"]
            else:
                estado_options = ["Sin cursos asociados"]

            selected_estados = st.multiselect(
                "Estado",
                options=estado_options,
                default=st.session_state.course_filters.get("Estado", []),
                placeholder="Elige un Estado",
                key="estado_course_filter"
            )
            st.session_state.course_filters["Estado"] = selected_estados

    with col2:
        # Gerencia filter
        if "Gerencia" in df.columns:
            gerencias = sorted(df["Gerencia"].dropna().unique())
            selected_gerencias = st.multiselect(
                "Gerencia",
                options=gerencias,
                default=st.session_state.course_filters.get("Gerencia", []),
                placeholder="Elige una Gerencia",
                key="gerencia_course_filter"
            )
            st.session_state.course_filters["Gerencia"] = selected_gerencias

    with col3:
        # Audiencia filter
        if "Audiencia" in df.columns:
            audiencias = sorted(df["Audiencia"].dropna().unique())
            selected_audiencias = st.multiselect(
                "Audiencia",
                options=audiencias,
                default=st.session_state.course_filters.get("Audiencia", []),
                placeholder="Elige una Audiencia",
                key="audiencia_course_filter"
            )
            st.session_state.course_filters["Audiencia"] = selected_audiencias

    with col4:
        # Prioridad filter
        if "Prioridad" in df.columns:
            prioridades = sorted(df["Prioridad"].dropna().unique())
            selected_prioridades = st.multiselect(
                "Prioridad",
                options=prioridades,
                default=st.session_state.course_filters.get("Prioridad", []),
                placeholder="Elige una Prioridad",
                key="prioridad_course_filter"
            )
            st.session_state.course_filters["Prioridad"] = selected_prioridades

    # Clear filters button
    col_clear, col_space = st.columns([1, 3])
    with col_clear:
        if st.button("🗑️ Limpiar Filtros", type="primary"):
            st.session_state.course_filters = {}
            st.rerun()

