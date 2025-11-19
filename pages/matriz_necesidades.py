import streamlit as st
import pandas as pd
import time
from src.data.database_utils import download_demo_db, import_excel_to_database, generate_excel_template, fetch_matrix, get_matrix_metrics
from src.forms.modify_matrix_form import show_edit_matrix_dialog
from src.forms.add_matrix_form import add_initiative_form, validate_add_form_info, save_new_initiative
from src.forms.delete_matrix_form import show_delete_matrix_dialog
from src.utils.matrix_utils import show_filters, reload_data, format_asociacion
from src.utils.download_utils import download_excel_button

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
st.title("Matriz de Necesidades de Aprendizaje")

# Create tabs for different functionalities
tab1, tab2, tab3, tab4 = st.tabs(["📊 Ver Matriz", "✏️ Editar", "➕ Agregar", "🗑️ Eliminar"])

# Initialize session state for filters
if "filters" not in st.session_state:
    st.session_state.filters = {}

# Initialize global dialog lock to prevent multiple dialogs
if "dialog_active" not in st.session_state:
    st.session_state.dialog_active = False

with tab1:
    # Reload data to ensure we have the latest changes
    df = reload_data()

    # Add Asociación column based on LinkedIn course presence (positioned as third column)
    if not df.empty:
        df.insert(3, 'Asociación', df.apply(format_asociacion, axis=1))        

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
                elif column == "Validación":
                    # Special handling for Validación filter
                    if "✅ Validado" in selected_values and "❌ Pendiente" in selected_values:
                        # Both selected - show all rows
                        pass
                    elif "✅ Validado" in selected_values:
                        # Only show validated rows
                        filtered_df = filtered_df[filtered_df["Validación"].str.contains("✅ Validado", na=False)]
                    elif "❌ Pendiente" in selected_values:
                        # Only show unvalidated rows
                        filtered_df = filtered_df[filtered_df["Validación"].str.contains("❌ Pendiente", na=False)]
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
            validacion_filter=current_filters.get("Validación"),
            asociaciones_filter=current_filters.get("Asociaciones")            
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("🎯 Cantidad de Actividades Formativas", metrics["activities"], border=True)

        with col2:
            st.metric("✅ Actividades Formativas Validadas", metrics["validated"], border=True)

        with col3:
            if metrics["activities"] > 0:
                coverage_pct = round((metrics["linkedin"] / metrics["activities"]) * 100, 1)
                st.metric("📈 Asociación de Actividades a Cursos", f"{coverage_pct}%", border=True)

        with col4:
            st.metric("🌐 Cantidad de Cursos LinkedIn", metrics["linkedin"], border=True)

        # Display filtered dataframe
        if not filtered_df.empty:
            st.markdown(f"**Mostrando {len(filtered_df)} de {len(df)} registros**")
                    
            # Download button section
            download_excel_button(
                filtered_df,
                filename="matriz_necesidades_filtrada.xlsx",
                button_text_prefix="📥 Descargar"
            )

            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": None,  # Hide the id column
                    "Curso Sugerido LinkedIn": None,  # Hide the LinkedIn course column since we show it in Asociación
                    "Validación": st.column_config.TextColumn(
                        "Validación",
                        help="Estado de validación de la actividad formativa",
                        width="small"
                    ),
                    "Asociación": st.column_config.TextColumn(
                        "Asociación",
                        help="Muestra el curso de LinkedIn asociado (🌐) o indica que no hay asociación (❌)",
                        width="medium"
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
        st.markdown("**Carga una base de datos de ejemplo:**")
        
        # Add data to the matrix (example database)
        if st.button("🔄 Cargar base de datos de ejemplo", type="primary"):
            success, message = download_demo_db()
            if success:
                st.success("Base de datos cargada correctamente.")
                time.sleep(3)
                st.rerun()
            else:
                st.error(f"Error al descargar la base de datos: {message}")
        
        # Add data to the matrix (upload Excel)
        st.markdown("**O carga tu propio archivo Excel:**")
        
        # Download template button
        template_data = generate_excel_template()
        st.download_button(
            label="📥 Descargar plantilla Excel",
            data=template_data,
            file_name="plantilla_matriz_necesidades.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Descarga una plantilla Excel vacía con todas las columnas necesarias para importar datos."
        )
        
        uploaded_file = st.file_uploader(
            "Subir archivo Excel",
            type=['xlsx', 'xls'],
            help="Sube un archivo Excel (.xlsx o .xls) con las columnas de la matriz. El archivo será validado antes de importar los datos.",
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            if st.button("📤 Importar archivo Excel", type="primary", use_container_width=True):
                success, message, imported_count = import_excel_to_database(uploaded_file)
                if success:
                    st.success(message)
                    time.sleep(3)
                    st.rerun()
                else:
                    st.error(message)

with tab2:
    # Reload data to ensure we have the latest changes
    df = reload_data()

    # Add Asociación column for consistency with ver matriz tab
    if not df.empty:
        df.insert(3, 'Asociación', df.apply(format_asociacion, axis=1))

    # Edit functionality
    if not df.empty:
        st.markdown("""Por favor, selecciona una fila para editar:""")

        # Initialize session state for edit dialog tracking
        if "edit_matrix_dialog_open" not in st.session_state:
            st.session_state.edit_matrix_dialog_open = False

        # Determine dataframe key based on dialog state
        # When dialog closes, we change the key to reset selection
        edit_dialog_was_open = st.session_state.edit_matrix_dialog_open
        st.session_state.edit_matrix_dialog_open = False  # Reset for this render

        # If dialog was previously open, it has now closed, so reset the global lock
        if edit_dialog_was_open:
            st.session_state.dialog_active = False

        # Use different keys to reset selection when dialog closes
        dataframe_key = "edit_matrix_dialog_closed" if edit_dialog_was_open else "edit_matrix_normal"

        edited_matrix = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": None,  # Hide the id column
                "Curso Sugerido LinkedIn": None,  # Hide the LinkedIn course column since we show it in Asociación
                "Validación": st.column_config.TextColumn(
                    "Validación",
                    help="Estado de validación de la actividad formativa",
                    width="small"
                ),
                "Asociación": st.column_config.TextColumn(
                    "Asociación",
                    help="Muestra el curso de LinkedIn asociado (✅) o indica que no hay asociación (❌)",
                    width="medium"
                ),
            },
            on_select="rerun",
            selection_mode="single-row",
            key=dataframe_key)

        # Check for row selection and show dialog
        selected_rows = edited_matrix.selection.get("rows", [])

        if selected_rows:
            # Get the selected row data
            row_data = df.iloc[selected_rows[0]]

            # Only show dialog if no other dialog is active
            if not st.session_state.dialog_active:
                # Mark dialog as open for next render and set global lock
                st.session_state.edit_matrix_dialog_open = True
                st.session_state.dialog_active = True

                # Show the dialog
                show_edit_matrix_dialog(row_data)

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

    # Add Asociación column for consistency with ver matriz tab
    if not df.empty:
        df.insert(3, 'Asociación', df.apply(format_asociacion, axis=1))

    # Delete functionality
    if not df.empty:
        st.markdown("""Por favor, selecciona las filas para eliminar:""")

        # Initialize session state for delete dialog tracking
        if "delete_matrix_dialog_open" not in st.session_state:
            st.session_state.delete_matrix_dialog_open = False

        # Determine dataframe key based on dialog state
        # When dialog closes, we change the key to reset selection
        delete_dialog_was_open = st.session_state.delete_matrix_dialog_open
        st.session_state.delete_matrix_dialog_open = False  # Reset for this render

        # If dialog was previously open, it has now closed, so reset the global lock
        if delete_dialog_was_open:
            st.session_state.dialog_active = False

        # Use different keys to reset selection when dialog closes
        delete_dataframe_key = "delete_matrix_dialog_closed" if delete_dialog_was_open else "delete_matrix_normal"

        delete_matrix = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": None,  # Hide the id column
                "Curso Sugerido LinkedIn": None,  # Hide the LinkedIn course column since we show it in Asociación
                "Validación": st.column_config.TextColumn(
                    "Validación",
                    help="Estado de validación de la actividad formativa",
                    width="small"
                ),
                "Asociación": st.column_config.TextColumn(
                    "Asociación",
                    help="Muestra el curso de LinkedIn asociado (✅) o indica que no hay asociación (❌)",
                    width="medium"
                ),
            },
            on_select="rerun",
            selection_mode="multi-row",
            key=delete_dataframe_key)

        # Check for row selection and trigger delete dialog
        selected_rows = delete_matrix.selection.get("rows", [])

        if selected_rows:
            # Get all selected row data
            selected_data = df.iloc[selected_rows]

            # Only show dialog if no other dialog is active
            if not st.session_state.dialog_active:
                # Mark dialog as open for next render and set global lock
                st.session_state.delete_matrix_dialog_open = True
                st.session_state.dialog_active = True

                # Show delete confirmation dialog
                show_delete_matrix_dialog(selected_data, df)

        else:
            st.info("👆 Selecciona una o más filas para eliminarlas.")

    else:
        st.warning("No hay datos disponibles para eliminar.")