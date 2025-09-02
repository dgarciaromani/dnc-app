import streamlit as st
import pandas as pd
import altair as alt
from utils.database_utils import (
    get_respondents,
    get_raw_data_forms,
    fetch_plan,
    get_linkedin_courses
)
from utils.dashboard_utils import create_donut_chart, get_dashboard_data

st.set_page_config(layout="wide", page_title="Dashboard DNC", page_icon="📊")
st.title("Dashboard DNC")

# Get all dashboard data
try:
    data = get_dashboard_data()

    # Summary metrics using Streamlit's metric component
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_respondents = len(get_respondents())
        st.metric("👥 Total Encuestados", total_respondents)

    with col2:
        total_needs = len(get_raw_data_forms())
        st.metric("📋 Necesidades Levantadas", total_needs)

    with col3:
        total_activities = len(fetch_plan())
        st.metric("🎯 Actividades Formativas", total_activities)

    with col4:
        linkedin_courses = len(get_linkedin_courses())
        st.metric("🎓 Cursos LinkedIn", linkedin_courses)

    # Respondents Analysis
    st.header("👥 Análisis de Encuestados")
    if not data['respondents_by_gerencia'].empty:
        chart = create_donut_chart(
            data['respondents_by_gerencia'],
            "Distribución de Encuestados por Gerencia",
            'reds'
        )
        st.altair_chart(chart, use_container_width=False)
    else:
        st.info("No hay datos de encuestados disponibles")

    # Needs Analysis
    st.header("📋 Análisis de Necesidades")

    col1, col2 = st.columns(2)

    with col1:
        if not data['needs_by_challenge'].empty:
            chart = create_donut_chart(
                data['needs_by_challenge'],
                "Necesidades por Desafío Estratégico",
                'greens'
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No hay datos de desafíos")

        if not data['needs_by_audience'].empty:
            chart = create_donut_chart(
                data['needs_by_audience'],
                "Necesidades por Audiencia",
                'blues'
            )
            st.altair_chart(chart, use_container_width=False)
        else:
            st.info("No hay datos de audiencias")

    with col2:
        if not data['needs_by_priority'].empty:
            chart = create_donut_chart(
                data['needs_by_priority'],
                "Necesidades por Prioridad",
                'oranges'
            )
            st.altair_chart(chart, use_container_width=False)
        else:
            st.info("No hay datos de prioridades")
        

    # Strategic Challenges
    

    # Training Activities Analysis
    st.header("🎯 Análisis de Actividades Formativas")

    col1, col2, col3 = st.columns(3)

    with col1:
        if not data['activities_by_modality'].empty:
            chart = create_donut_chart(
                data['activities_by_modality'],
                "Actividades por Modalidad",
                'purples'
            )
            st.altair_chart(chart, use_container_width=False)
        else:
            st.info("No hay datos de modalidades")

    with col2:
        if not data['activities_by_priority'].empty:
            chart = create_donut_chart(
                data['activities_by_priority'],
                "Actividades por Prioridad",
                'teals'
            )
            st.altair_chart(chart, use_container_width=False)
        else:
            st.info("No hay datos de prioridades de actividades")

    with col3:
        if not data['activities_by_audience'].empty:
            chart = create_donut_chart(
                data['activities_by_audience'],
                "Actividades por Audiencia",
                'browns'
            )
            st.altair_chart(chart, use_container_width=False)
        else:
            st.info("No hay datos de audiencias de actividades")

    # LinkedIn Courses Analysis
    st.header("🎓 Análisis de Cursos LinkedIn")
    if not data['linkedin_usage'].empty:
        chart = create_donut_chart(
            data['linkedin_usage'],
            "Actividades con Cursos LinkedIn Asociados",
            'paired'
        )
        st.altair_chart(chart, use_container_width=False)
    else:
        st.info("No hay datos de cursos LinkedIn")

    # Time Trends
    st.header("📈 Tendencias Temporales")
    if not data['time_trends'].empty:
        # Convert date strings to datetime
        data['time_trends']['date'] = pd.to_datetime(data['time_trends']['date'])

        line_chart = alt.Chart(data['time_trends']).mark_line(
            point=True,
            color='#ff4b4b',
            strokeWidth=3
        ).encode(
            x=alt.X('date:T', title='Fecha'),
            y=alt.Y('submissions:Q', title='Número de Envíos'),
            tooltip=['date:T', 'submissions:Q']
        ).properties(
            title="Tendencia de Envíos de Necesidades a lo Largo del Tiempo",
            width=800,
            height=400
        )

        st.altair_chart(line_chart, use_container_width=True)
    else:
        st.info("No hay datos temporales disponibles")

except Exception as e:
    st.error(f"Error al cargar los datos del dashboard: {str(e)}")
    st.info("Asegúrese de que la base de datos esté correctamente configurada y contenga datos.")
