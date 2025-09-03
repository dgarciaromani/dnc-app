import streamlit as st
import pandas as pd
import time
import datetime
from utils.database_utils import download_demo_db, fetch_plan, update_final_plan, update_plan_linkedin_courses
from utils.edit_plan_form import get_row_data, validate_form_info, has_data_changed, get_id_from_name, gerencias, subgerencias, areas, desafios, audiencias, modalidades, fuentes, prioridades

# Authentication check
if not st.session_state.get("authenticated", False):
    st.error("❌ Acceso no autorizado. Por favor, inicie sesión.")
    st.stop()

# Initialize session state
if "edit_plan" not in st.session_state:
    st.session_state.edit_plan = False

# Make page use full width & set title
st.set_page_config(layout="wide")

# Load data
data = fetch_plan()
df = pd.DataFrame(data)

# Display only if there is data
if not df.empty and not st.session_state.edit_plan:
    st.title("Mi Plan de Formación")

    # Initialize session state for filters
    if "show_filters" not in st.session_state:
        st.session_state.show_filters = False
    if "filters" not in st.session_state:
        st.session_state.filters = {}

    # Toggle filters button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔍 Filtros" if not st.session_state.show_filters else "🔍 Ocultar Filtros"):
            st.session_state.show_filters = not st.session_state.show_filters
            st.rerun()
    with col2:
        if st.button("Editar Plan"):
            st.session_state.edit_plan = True
            st.rerun()

    # Filters section
    if st.session_state.show_filters:
        st.markdown("---")
        st.subheader("Filtros")

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
            if st.button("🗑️ Limpiar Filtros"):
                st.session_state.filters = {}
                st.rerun()

        st.markdown("---")

    # Apply filters to dataframe
    filtered_df = df.copy()

    # Apply each filter if selections exist
    for column, selected_values in st.session_state.filters.items():
        if selected_values:  # Only filter if values are selected
            filtered_df = filtered_df[filtered_df[column].isin(selected_values)]

    # Display filtered dataframe
    if not filtered_df.empty:
        st.markdown(f"**Mostrando {len(filtered_df)} de {len(df)} registros**")
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": None  # Hide the id column
            })
    else:
        st.info("No hay registros que coincidan con los filtros seleccionados.")
        if st.button("Mostrar todos los registros"):
            st.session_state.filters = {}
            st.rerun()

elif st.session_state.edit_plan:
    st.title("Mi Plan de Formación (editable)")

    if st.button("Volver al plan"):
        st.session_state.edit_plan = False
        st.rerun()

    st.markdown("""Por favor, selecciona la fila que deseas editar:""")
    edited_plan = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": None  # Hide the id column
        },
        on_select="rerun", 
        selection_mode="single-row")    

    # Check for row selection and display form
    selected_rows = edited_plan.selection.get("rows", [])
    if selected_rows:
        # Get the selected row data
        row_data = df.iloc[selected_rows[0]]
        st.subheader("Editar fila seleccionada")

        # Store original row data for comparison
        original_row = row_data.to_dict()

        # Display the form and handle submission
        save_clicked, form_info = get_row_data(row_data)

        if save_clicked:
            if not validate_form_info(form_info):
                st.error("Por favor completa todos los campos con (*).")
            else:
                # Check if data actually changed
                if has_data_changed(original_row, form_info):
                    try:
                        # Convert form data to database IDs
                        gerencia_id = get_id_from_name(gerencias, form_info['gerencia'])
                        subgerencia_id = get_id_from_name(subgerencias, form_info['subgerencia'])
                        area_id = get_id_from_name(areas, form_info['area'])
                        desafio_id = get_id_from_name(desafios, form_info['desafio'])
                        audiencia_id = get_id_from_name(audiencias, form_info['audiencia'])
                        modalidad_id = get_id_from_name(modalidades, form_info['modalidad'])
                        fuente_id = get_id_from_name(fuentes, form_info['fuente'])
                        prioridad_id = get_id_from_name(prioridades, form_info['prioridad'])

                        # Update the database
                        update_final_plan(
                            gerencia_id=gerencia_id,
                            subgerencia_id=subgerencia_id,
                            area_id=area_id,
                            desafio_id=desafio_id,
                            actividad=form_info['actividad_formativa'],
                            objetivo=form_info['objetivo_desempeno'],
                            contenidos=form_info['contenidos'],
                            skills=form_info['skills'],
                            keywords=form_info['keywords'],
                            modalidad_id=modalidad_id,
                            fuente_id=fuente_id,
                            fuente_interna=form_info['fuente_interna'],
                            audiencia_id=audiencia_id,
                            prioridad_id=prioridad_id,
                            plan_id=original_row['id']
                        )

                        # Update LinkedIn course (always call to handle None case for deletion)
                        update_plan_linkedin_courses(original_row['id'], form_info.get('linkedin'))

                        st.success("✅ Cambios guardados correctamente.")
                        time.sleep(2)
                        st.session_state.edit_plan = False
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error al guardar los cambios: {str(e)}")
                else:
                    st.info("ℹ️ No se detectaron cambios.")
                    time.sleep(2)
                    #st.session_state.edit_plan = False
                    st.rerun()
    else:
        st.info("👆 Selecciona una fila de la tabla para editarla.")

else:
    st.title("Mi Plan de Formación")
    st.info("Plan no disponible. Por favor, completa el cuestionario DNC para generar un plan de formación.")
    # Add data to the plan
    if st.button("Cargar base de datos de ejemplo"):
        success = download_demo_db()
        if success:
            st.success("Base de datos cargada correctamente.")
            time.sleep(3)
            st.rerun()
        else:
            st.error("No se pudo descargar la base de datos. Por favor, inténtalo nuevamente.")