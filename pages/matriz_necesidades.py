import streamlit as st
import pandas as pd
import time
from src.data.database_utils import download_demo_db, fetch_matrix, update_final_matrix, update_matrix_linkedin_courses, delete_matrix_entry, get_matrix_metrics
from src.forms.edit_matrix_form import get_row_data, validate_form_info, has_data_changed, get_id_from_name, gerencias, subgerencias, areas, desafios, audiencias, modalidades, fuentes, prioridades
from src.forms.add_initiative_form import add_initiative_form, validate_add_form_info, save_new_initiative
from src.utils.matrix_utils import show_filters, reload_data

# Authentication check
if not st.session_state.get("authenticated", False):
    st.error("❌ Acceso no autorizado. Por favor, inicie sesión.")
    st.stop()

# Make page use full width & set title
st.set_page_config(layout="wide")

# Load data
data = fetch_matrix()
df = pd.DataFrame(data)

# Main title
st.title("Mi Matriz de Necesidades de Aprendizaje")

# Create tabs for different functionalities
tab1, tab2, tab3, tab4 = st.tabs(["📊 Ver Matriz", "✏️ Editar", "➕ Agregar", "🗑️ Eliminar"])

# Initialize session state for filters
if "filters" not in st.session_state:
    st.session_state.filters = {}

with tab1:
    # Reload data to ensure we have the latest changes
    df = reload_data()

    # Add Asociación column based on LinkedIn course presence (positioned as second column)
    if not df.empty:
        # Insert at specific position
        asociacion_values = df['Curso Sugerido LinkedIn'].apply(
            lambda x: "✅" if pd.notna(x) and x.strip() != "" else "❌"
        )
        df.insert(2, 'Asociación', asociacion_values)

    # Display only if there is data
    if not df.empty:

        # Filters section with expander
        with st.expander("🔍 Filtros", expanded=False):
            show_filters(df)

        # Apply filters to dataframe
        filtered_df = df.copy()

        # Apply each filter if selections exist
        for column, selected_values in st.session_state.filters.items():
            if selected_values:  # Only filter if values are selected
                if column == "Asociaciones":
                    # Special handling for Asociaciones filter
                    linkedin_col = "Curso Sugerido LinkedIn"
                    if "Con cursos asociados" in selected_values and "Sin cursos asociados" in selected_values:
                        # Both selected - show all rows
                        pass
                    elif "Con cursos asociados" in selected_values:
                        # Only show rows with LinkedIn courses
                        filtered_df = filtered_df[filtered_df[linkedin_col].notna() & (filtered_df[linkedin_col] != "")]
                    elif "Sin cursos asociados" in selected_values:
                        # Only show rows without LinkedIn courses
                        filtered_df = filtered_df[filtered_df[linkedin_col].isna() | (filtered_df[linkedin_col] == "")]
                else:
                    # Normal filter logic for other columns
                    filtered_df = filtered_df[filtered_df[column].isin(selected_values)]

        # Calculate metrics based on filtered data
        current_filters = st.session_state.get("filters", {})
        metrics = get_matrix_metrics(
            gerencia_filter=current_filters.get("Gerencia"),
            subgerencia_filter=current_filters.get("Subgerencia"),
            area_filter=current_filters.get("Área"),
            desafio_filter=current_filters.get("Desafío Estratégico"),
            audiencia_filter=current_filters.get("Audiencia"),
            modalidad_filter=current_filters.get("Modalidad"),
            fuente_filter=current_filters.get("Fuente"),
            prioridad_filter=current_filters.get("Prioridad"),
            asociaciones_filter=current_filters.get("Asociaciones")
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("🎯 Cantidad de Actividades Formativas", metrics["activities"], border=True)

        with col2:
            st.metric("🎓 Cantidad de Cursos LinkedIn", metrics["linkedin"], border=True)

        with col3:
            if metrics["activities"] > 0:
                coverage_pct = round((metrics["linkedin"] / metrics["activities"]) * 100, 1)
                st.metric("📈 Asignación de Actividades Formativas a Cursos", f"{coverage_pct}%", border=True)

        # Display filtered dataframe
        if not filtered_df.empty:
            st.markdown(f"**Mostrando {len(filtered_df)} de {len(df)} registros**")
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": None,  # Hide the id column
                    "Asociación": st.column_config.TextColumn(
                        "Asociación",
                        help="Indica si hay un curso de LinkedIn asociado",
                        width="small"
                    ),
                },
                key="view_matrix_dataframe")
        else:
            st.info("No hay registros que coincidan con los filtros seleccionados.")
            if st.button("↩️ Mostrar todos los registros", type="primary"):
                st.session_state.filters = {}
                st.rerun()
    else:
        st.info("Matriz no disponible. Por favor, completa el cuestionario DNC para generar una matriz de necesidades de aprendizaje.")
        # Add data to the matrix
        if st.button("🔄 Cargar base de datos de ejemplo", type="primary"):
            success, message = download_demo_db()
            if success:
                st.success("Base de datos cargada correctamente.")
                time.sleep(3)
                st.rerun()
            else:
                st.error(f"Error al descargar la base de datos: {message}")

with tab2:
    # Reload data to ensure we have the latest changes
    df = reload_data()

    # Edit functionality
    if not df.empty:
        st.markdown("""Por favor, selecciona una fila para editar:""")
        edited_matrix = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": None,  # Hide the id column
            },
            on_select="rerun",
            selection_mode="single-row",
            key="edit_matrix_dataframe")

        # Check for row selection and display form
        selected_rows = edited_matrix.selection.get("rows", [])

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
                            update_final_matrix(
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
                                matrix_id=original_row['id']
                            )

                            # Update LinkedIn course (always call to handle None case for deletion)
                            update_matrix_linkedin_courses(original_row['id'], form_info.get('linkedin'))

                            st.success("✅ Cambios guardados correctamente.")
                            time.sleep(2)
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error al guardar los cambios: {str(e)}")
                    else:
                        st.info("ℹ️ No se detectaron cambios.")
                        time.sleep(2)
                        st.rerun()
        else:
            st.info("👆 Selecciona una fila de la tabla para editarla.")
    else:
        st.warning("No hay datos disponibles para editar.")

with tab3:
    # Add initiative functionality
    st.subheader("Agregar nueva iniciativa")
    st.markdown("""Completa el siguiente formulario para agregar una nueva iniciativa de formación:""")

    # Display the form
    submitted, form_data = add_initiative_form()

    # Handle form submission
    if submitted:
        if not validate_add_form_info(form_data):
            st.error("❌ Por favor completa todos los campos marcados con (*).")
        else:
            # Save the new initiative
            success = save_new_initiative(form_data)

            if success:
                st.success("✅ Nueva iniciativa agregada correctamente.")
                time.sleep(2)
                st.rerun()
            else:
                st.error("❌ Error al guardar la nueva iniciativa.")

with tab4:
    # Reload data to ensure we have the latest changes
    df = reload_data()

    # Delete functionality
    if not df.empty:
        st.markdown("""Por favor, selecciona las filas para eliminar:""")
        delete_matrix = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": None,  # Hide the id column
            },
            on_select="rerun",
            selection_mode="multi-row",
            key="delete_matrix_dataframe")

        # Check for row selection and display delete confirmation
        selected_rows = delete_matrix.selection.get("rows", [])

        if selected_rows:
            # Get all selected row data
            selected_data = df.iloc[selected_rows]
            
            st.subheader("Resumen de filas a eliminar:")
            st.dataframe(selected_data[['Gerencia', 'Desafío Estratégico', 'Actividad Formativa', 'Audiencia']])

            st.warning("⚠️ **ATENCIÓN:** Esta acción no se puede deshacer.")

            # Delete confirmation
            if st.button(f"🗑️ Confirmar Eliminación de {len(selected_rows)} fila(s)", type="primary"):
                try:
                    for row in selected_rows:
                        delete_matrix_entry(int(df.iloc[row]['id']))
                    st.success(f"✅ {len(selected_rows)} fila(s) eliminada(s) correctamente.")
                    time.sleep(2)
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error al eliminar las filas: {str(e)}")

        else:
            st.info("👆 Selecciona una o más filas para eliminarlas.")

    else:
        st.warning("No hay datos disponibles para eliminar.")