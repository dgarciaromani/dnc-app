import streamlit as st
import time
from src.data.database_utils import validate_matrix_entry, unvalidate_matrix_entry


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


def show_validation_dialog(selected_data):
    @st.dialog("✅ Actividades seleccionadas para validación", width="large")
    def validation_dialog():
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
                f"✅ Validar {len(selected_data)} actividad(es)",
                type="primary"
            )

            if submitted:
                try:
                    validated_count = 0
                    for _, row_data in selected_data.iterrows():
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

    # Show the dialog
    validation_dialog()


def show_unvalidation_dialog(selected_data):
    @st.dialog("❌ Remover Validación - Actividades seleccionadas", width="large")
    def unvalidation_dialog():
        st.dataframe(
            selected_data[['Gerencia', 'Desafío Estratégico', 'Actividad Formativa', 'Audiencia', 'Validación']],
            use_container_width=True,
            hide_index=True
        )

        # Unvalidation form
        with st.form("unvalidation_form"):
            st.subheader("Detalles de Remoción de Validación")

            # Display the unvalidator's name (non-editable)
            st.markdown(f"**Validación removida por:** {st.session_state.name}")
            unvalidated_by = st.session_state.name

            unvalidation_notes = st.text_area(
                "Notas de remoción de validación:",
                height=100,
                help="Comentarios adicionales sobre la remoción de validación"
            )

            st.warning("⚠️ **ATENCIÓN:** Esta acción removerá permanentemente el estado de validación de las actividades seleccionadas.")

            submitted = st.form_submit_button(
                f"❌ Remover Validación de {len(selected_data)} actividad(es)",
                type="secondary"
            )

            if submitted:
                try:
                    unvalidated_count = 0
                    for _, row_data in selected_data.iterrows():
                        unvalidate_matrix_entry(
                            matrix_id=row_data['id']
                        )
                        unvalidated_count += 1

                    st.success(f"✅ Validación removida de {unvalidated_count} actividad(es) correctamente.")
                    time.sleep(2)
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error durante la remoción de validación: {str(e)}")

    # Show the dialog
    unvalidation_dialog()