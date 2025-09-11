import streamlit as st
import pandas as pd
import altair as alt
from src.utils.dashboard_utils import create_pie_chart, create_horizontal_bar_chart, create_vertical_bar_chart
from src.data.dashboard_queries import get_dashboard_data, get_origin_filtered_data, get_available_origins, get_summary_metrics

# Authentication check
if not st.session_state.get("authenticated", False):
    st.error("❌ Acceso no autorizado. Por favor, inicie sesión.")
    st.stop()

st.set_page_config(layout="wide")
st.title("Dashboard DNC")

# Get all dashboard data
try:
    # Get complete data for origins overview (always shows full data)
    complete_data = get_dashboard_data()

    st.subheader("📊 Visión General")

    # Two-column layout: Origins chart on left, filters on right
    col_chart, col_filters = st.columns([1, 1])

    with col_chart:
        if not complete_data['origin_of_needs'].empty:
            # Center the chart in the column
            col_empty1, col_chart_center, col_empty2 = st.columns([0.15, 0.7, 0.15])
            with col_chart_center:
                pie_chart = create_pie_chart(complete_data['origin_of_needs'], "Origen de las Necesidades de Capacitación", 'viridis')
                st.altair_chart(pie_chart, use_container_width=True)
        else:
            st.info("No hay datos disponibles")

    # FILTERED ANALYSIS SECTION
    with col_filters:
        # Get available origins for filtering
        available_origins = get_available_origins()
        all_origins = ["Todos"] + available_origins

        # Origin filter
        selected_origin = st.selectbox(
            "🔍 Filtrar por Origen:",
            options=all_origins,
            index=0,
            help="Selecciona un origen para filtrar todos los gráficos, o 'Todos' para ver datos completos"
        )

        # Get filtered data based on selection
        data = get_origin_filtered_data(selected_origin)

        # Show current filter status
        if selected_origin != "Todos":
            st.info(f"Mostrando datos filtrados por origen: **{selected_origin}**")
        else:
            st.info("Mostrando datos de todos los orígenes")

    # Summary metrics using Streamlit's metric component (full width)
    st.divider()  # Separate header from main content
    metrics = get_summary_metrics(selected_origin)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🎯 Cantidad de Actividades Formativas", metrics["activities"], border=True)

    with col2:
        st.metric("🎓 Cantidad de Cursos LinkedIn", metrics["linkedin"], border=True)

    with col3:
        if selected_origin in ["DNC", "Todos"]:
            st.metric("👤 Cantidad de Personas Encuestadas", metrics["respondents"], border=True)
        
    with col4:
        if selected_origin in ["DNC", "Todos"]:
            st.metric("📋 Cantidad de Necesidades Levantadas", metrics["needs"], border=True)

    # Main content area with all charts
    # Activities by Gerencia Analysis
    with st.expander("🏢 Actividades por Gerencia, Subgerencia, Área y Audiencia"):
        col1, col2 = st.columns(2)

        with col1:
            if not data['activities_by_gerencia'].empty:
                chart = create_horizontal_bar_chart(
                    data['activities_by_gerencia'],
                    "Actividades en la Matriz de Necesidades por Gerencia",
                    'reds'
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No hay datos disponibles")

            if not data['activities_by_area'].empty:
                chart = create_horizontal_bar_chart(
                    data['activities_by_area'],
                    "Actividades en la Matriz de Necesidades por Área",
                    'greens'
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No hay datos de áreas")

        with col2:
            if not data['activities_by_subgerencia'].empty:
                chart = create_horizontal_bar_chart(
                    data['activities_by_subgerencia'],
                    "Actividades en la Matriz de Necesidades por Subgerencia",
                    'blues'
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No hay datos de subgerencias")

            if not data['activities_by_audience'].empty:
                chart = create_horizontal_bar_chart(
                    data['activities_by_audience'],
                    "Necesidades por Audiencia",
                    'browns'
                )
                st.altair_chart(chart, use_container_width=False)
            else:
                st.info("No hay datos de audiencias")

    # Actividades por Desafío Estratégico y Prioridad
    with st.expander("🎯 Actividades por Desafío Estratégico y Prioridad"):
        col1, col2 = st.columns(2)

        with col1:
            if not data['activities_by_challenge'].empty:
                chart = create_horizontal_bar_chart(
                    data['activities_by_challenge'],
                    "Necesidades por Desafío Estratégico",
                    'purples'
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No hay datos de desafíos")

        with col2:
            if not data['activities_by_priority'].empty:
                chart = create_vertical_bar_chart(
                    data['activities_by_priority'],
                    "Necesidades por Prioridad",
                    'teals'
                )
                st.altair_chart(chart, use_container_width=False)
            else:
                st.info("No hay datos de prioridades")

    # Actividades Formativas por Modalidad y Audiencia
    with st.expander("🚀 Actividades Formativas por Modalidad y Fuente"):
        col1, col2 = st.columns(2)

        with col1:
            if not data['activities_by_modality'].empty:
                chart = create_vertical_bar_chart(
                    data['activities_by_modality'],
                    "Actividades por Modalidad",
                    'warmgreys'
                )
                st.altair_chart(chart, use_container_width=False)
            else:
                st.info("No hay datos de modalidades")

        with col2:
            if not data['activities_by_source'].empty:
                chart = create_vertical_bar_chart(
                    data['activities_by_source'],
                    "Actividades por Fuente",
                    'oranges'
                )
                st.altair_chart(chart, use_container_width=False)
            else:
                st.info("No hay datos de fuentes")

    # LinkedIn Courses Analysis
    with st.expander("🎓 Análisis de Cursos LinkedIn"):
        col1, col2 = st.columns(2)

        with col1:
            if not data['linkedin_usage'].empty:
                chart = create_pie_chart(
                    data['linkedin_usage'],
                    "Actividades con Cursos LinkedIn Asociados",
                    'paired'
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No hay datos de cursos LinkedIn")

    # Time Trends
    if selected_origin in ["DNC", "Todos"]:
        with st.expander("📈 Tendencia de Levantamiento de Necesidades en el tiempo"):
            if not data['time_trends'].empty:
                # Convert date strings to datetime
                data['time_trends']['Fecha'] = pd.to_datetime(data['time_trends']['Fecha'])

                line_chart = alt.Chart(data['time_trends']).mark_line(
                    point=True,
                    color='#ff4b4b',
                    strokeWidth=3
                ).encode(
                    x=alt.X('Fecha:T', title='Fecha'),
                    y=alt.Y('Envíos:Q', title='Número de Envíos'),
                    tooltip=['Fecha:T', 'Envíos:Q']
                ).properties(
                    title="Tendencia de Envíos de Necesidades a lo Largo del Tiempo",
                    width=800,
                    height=400
                )

                st.altair_chart(line_chart, use_container_width=True)
            else:
                st.info("No hay datos temporales disponibles")

            if not data['monthly_trends'].empty:
                st.dataframe(data['monthly_trends'], use_container_width=True)
            else:
                st.info("No hay datos mensuales disponibles")

except Exception as e:
    st.error(f"Error al cargar los datos del dashboard: {str(e)}")
    st.info("Asegúrese de que la base de datos esté correctamente configurada y contenga datos.")
