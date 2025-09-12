import streamlit as st
import pandas as pd
import time
from src.data.database_utils import fetch_matrix, validate_matrix_entry, unvalidate_matrix_entry
from src.utils.matrix_utils import reload_data
from src.utils.validar_utils import show_validation_filters

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
st.title("Validación de Necesidades de Aprendizaje")

# Create tabs for different validation functionalities
tab1, tab2, tab3 = st.tabs(["✅ Necesidades Validadas", "📋 Pendientes de Validación", "🔄 Remover Validación"])

# Session state is initialized within each tab

with tab1:
    # Reload data to ensure we have the latest changes
    df = reload_data()

    # Filter for validated activities only
    if not df.empty:
        validated_df = df[df['Validación'].str.contains('✅ Validado', na=False)]

        if not validated_df.empty:
            # Add Asociación column
            asociacion_values = validated_df['Curso Sugerido LinkedIn'].apply(
                lambda x: "✅ LinkedIn" if pd.notna(x) and x.strip() != "" else "❌"
            )
            validated_df.insert(3, 'Asociación', asociacion_values)

            st.markdown(f"**Total de actividades validadas: {len(validated_df)}**")

            # Filters section
            with st.expander("🔍 Filtros", expanded=False):
                # Create a copy of the dataframe for filtering
                filter_df = validated_df.copy()

                # Use separate filter keys for validated tab
                if "validation_filters_validated" not in st.session_state:
                    st.session_state.validation_filters_validated = {}

                # Show filters with unique keys for validation page
                show_validation_filters(filter_df, tab_prefix="validated", session_state_key="validation_filters_validated")

                # Apply filters
                for column, selected_values in st.session_state.validation_filters_validated.items():
                    if selected_values:
                        if column == "Asociaciones":
                            # Special handling for Asociaciones filter
                            linkedin_col = "Curso Sugerido LinkedIn"
                            if "Con cursos asociados" in selected_values and "Sin cursos asociados" in selected_values:
                                # Both selected - show all rows
                                pass
                            elif "Con cursos asociados" in selected_values:
                                # Only show rows with LinkedIn courses
                                validated_df = validated_df[validated_df[linkedin_col].notna() & (validated_df[linkedin_col] != "")]
                            elif "Sin cursos asociados" in selected_values:
                                # Only show rows without LinkedIn courses
                                validated_df = validated_df[validated_df[linkedin_col].isna() | (validated_df[linkedin_col] == "")]
                        elif column in validated_df.columns:
                            # Normal filter logic for other columns
                            validated_df = validated_df[validated_df[column].isin(selected_values)]

            # Display validated activities
            st.dataframe(
                validated_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": None,
                    "Asociación": st.column_config.TextColumn(
                        "Asociación",
                        help="Indica si hay un curso de LinkedIn asociado",
                        width="small"
                    ),
                    "Validación": st.column_config.TextColumn(
                        "Validación",
                        help="Estado de validación de la actividad formativa",
                        width="small"
                    ),
                },
                key="validated_activities_dataframe"
            )
        else:
            st.info("No hay actividades validadas aún.")
    else:
        st.info("No hay datos disponibles.")

with tab2:
    # Reload data to ensure we have the latest changes
    df = reload_data()

    if not df.empty:
        # Filter for unvalidated activities
        unvalidated_df = df[df['Validación'].str.contains('❌ Pendiente', na=False)]

        if not unvalidated_df.empty:
            # Add Asociación column for better context
            asociacion_values = unvalidated_df['Curso Sugerido LinkedIn'].apply(
                lambda x: "✅ LinkedIn" if pd.notna(x) and x.strip() != "" else "❌"
            )
            unvalidated_df.insert(3, 'Asociación', asociacion_values)

            st.markdown(f"**Actividades pendientes: {len(unvalidated_df)}**")

            # Filters section
            with st.expander("🔍 Filtros", expanded=False):
                # Create a copy of the dataframe for filtering
                filter_df = unvalidated_df.copy()

                # Use separate filter keys for validation page
                if "validation_filters_pending" not in st.session_state:
                    st.session_state.validation_filters_pending = {}

                # Show filters with unique keys for validation page
                show_validation_filters(filter_df, tab_prefix="pending", session_state_key="validation_filters_pending")

                # Apply filters
                for column, selected_values in st.session_state.validation_filters_pending.items():
                    if selected_values:
                        if column == "Asociaciones":
                            # Special handling for Asociaciones filter
                            linkedin_col = "Curso Sugerido LinkedIn"
                            if "Con cursos asociados" in selected_values and "Sin cursos asociados" in selected_values:
                                # Both selected - show all rows
                                pass
                            elif "Con cursos asociados" in selected_values:
                                # Only show rows with LinkedIn courses
                                unvalidated_df = unvalidated_df[unvalidated_df[linkedin_col].notna() & (unvalidated_df[linkedin_col] != "")]
                            elif "Sin cursos asociados" in selected_values:
                                # Only show rows without LinkedIn courses
                                unvalidated_df = unvalidated_df[unvalidated_df[linkedin_col].isna() | (unvalidated_df[linkedin_col] == "")]
                        elif column in unvalidated_df.columns:
                            # Normal filter logic for other columns
                            unvalidated_df = unvalidated_df[unvalidated_df[column].isin(selected_values)]

            # Validation interface
            st.subheader("Seleccionar actividades para validar")

            validation_df = st.dataframe(
                unvalidated_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": None,  # Hide the id column
                    "Asociación": st.column_config.TextColumn(
                        "Asociación",
                        help="Indica si hay un curso de LinkedIn asociado",
                        width="small"
                    ),
                    "Validación": st.column_config.TextColumn(
                        "Validación",
                        help="Estado de validación de la actividad formativa",
                        width="small"
                    ),
                },
                on_select="rerun",
                selection_mode="multi-row",
                key="validation_pending_dataframe"
            )

            # Check for row selection
            selected_rows = validation_df.selection.get("rows", [])

            if selected_rows:
                # Get selected data
                selected_data = unvalidated_df.iloc[selected_rows]

                st.subheader("Actividades seleccionadas para validación:")
                st.dataframe(
                    selected_data[['Gerencia', 'Desafío Estratégico', 'Actividad Formativa', 'Audiencia', 'Validación']],
                    use_container_width=True,
                    hide_index=True
                )

                # Validation form
                with st.form("validation_form"):
                    st.subheader("Detalles de Validación")

                    # Display the validator's name (non-editable)
                    st.markdown(f"**Validado por:** {st.session_state.name}")
                    validated_by = st.session_state.name

                    validation_notes = st.text_area(
                        "Notas de validación:",
                        height=100,
                        help="Comentarios adicionales sobre la validación"
                    )

                    submitted = st.form_submit_button(
                        f"✅ Validar {len(selected_rows)} actividad(es)",
                        type="primary"
                    )

                    if submitted:
                        try:
                            validated_count = 0
                            for row_idx in selected_rows:
                                row_data = unvalidated_df.iloc[row_idx]
                                validate_matrix_entry(
                                    matrix_id=row_data['id'],
                                    validated_by=validated_by,
                                    validation_notes=validation_notes.strip() if validation_notes.strip() else None
                                )
                                validated_count += 1

                            st.success(f"✅ {validated_count} actividad(es) validada(s) correctamente.")
                            time.sleep(2)
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error durante la validación: {str(e)}")

            else:
                st.info("👆 Selecciona una o más filas para validarlas.")
        else:
            st.success("🎉 ¡Todas las actividades están validadas!")
            st.info("No hay actividades pendientes de validación.")
    else:
        st.info("No hay datos disponibles.")

with tab3:
    # Reload data to ensure we have the latest changes
    df = reload_data()

    if not df.empty:
        # Filter for validated activities
        validated_df = df[df['Validación'].str.contains('✅ Validado', na=False)]

        if not validated_df.empty:
            # Add Asociación column
            asociacion_values = validated_df['Curso Sugerido LinkedIn'].apply(
                lambda x: "✅ LinkedIn" if pd.notna(x) and x.strip() != "" else "❌"
            )
            validated_df.insert(3, 'Asociación', asociacion_values)

            st.markdown(f"**Actividades que pueden tener su validación removida: {len(validated_df)}**")

            # Filters section
            with st.expander("🔍 Filtros", expanded=False):
                # Create a copy of the dataframe for filtering
                filter_df = validated_df.copy()

                # Use separate filter keys for remove validation tab
                if "validation_filters_remove" not in st.session_state:
                    st.session_state.validation_filters_remove = {}

                # Show filters with unique keys for remove validation
                show_validation_filters(filter_df, tab_prefix="remove", session_state_key="validation_filters_remove")

                # Apply filters
                for column, selected_values in st.session_state.validation_filters_remove.items():
                    if selected_values:
                        if column == "Asociaciones":
                            # Special handling for Asociaciones filter
                            linkedin_col = "Curso Sugerido LinkedIn"
                            if "Con cursos asociados" in selected_values and "Sin cursos asociados" in selected_values:
                                # Both selected - show all rows
                                pass
                            elif "Con cursos asociados" in selected_values:
                                # Only show rows with LinkedIn courses
                                validated_df = validated_df[validated_df[linkedin_col].notna() & (validated_df[linkedin_col] != "")]
                            elif "Sin cursos asociados" in selected_values:
                                # Only show rows without LinkedIn courses
                                validated_df = validated_df[validated_df[linkedin_col].isna() | (validated_df[linkedin_col] == "")]
                        elif column in validated_df.columns:
                            # Normal filter logic for other columns
                            validated_df = validated_df[validated_df[column].isin(selected_values)]

            # Display activities available for validation removal and handle selection
            remove_validation_df = st.dataframe(
                validated_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": None,
                    "Asociación": st.column_config.TextColumn(
                        "Asociación",
                        help="Indica si hay un curso de LinkedIn asociado",
                        width="small"
                    ),
                    "Validación": st.column_config.TextColumn(
                        "Validación",
                        help="Estado de validación de la actividad formativa",
                        width="small"
                    ),
                },
                on_select="rerun",
                selection_mode="multi-row",
                key="remove_validation_dataframe"
            )

            selected_for_removal = remove_validation_df.selection.get("rows", [])

            if selected_for_removal:
                selected_removal_data = validated_df.iloc[selected_for_removal]

                st.warning("⚠️ **ATENCIÓN:** Esta acción removerá el estado de validación de las actividades seleccionadas.")

                st.dataframe(
                    selected_removal_data[['Gerencia', 'Desafío Estratégico', 'Actividad Formativa', 'Audiencia']],
                    use_container_width=True,
                    hide_index=True
                )

                if st.button(f"❌ Remover Validación de {len(selected_for_removal)} actividad(es)", type="secondary"):
                    try:
                        removal_count = 0
                        for row_idx in selected_for_removal:
                            row_data = validated_df.iloc[row_idx]
                            unvalidate_matrix_entry(row_data['id'])
                            removal_count += 1

                        st.success(f"✅ Validación removida de {removal_count} actividad(es).")
                        time.sleep(2)
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error al remover validación: {str(e)}")

            else:
                st.info("👆 Selecciona actividades para remover su validación.")
        else:
            st.info("No hay actividades validadas para remover su validación.")
    else:
        st.info("No hay datos disponibles.")