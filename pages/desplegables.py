import streamlit as st
import pandas as pd
import time
from src.data import template_desplegables
from src.data.database_utils import fetch_all, edit_options, add_option, delete_option

# Authentication check
if not st.session_state.get("authenticated", False):
    st.error("❌ Acceso no autorizado. Por favor, inicie sesión.")
    st.stop()

# Initialize session state for data refresh tracking
if 'data_refresh_counter' not in st.session_state:
    st.session_state.data_refresh_counter = 0

st.title("Administrar desplegables")

# Selectbox tables
selected_table = st.selectbox(
    "Selecciona un desplegable",
    ["Selecciona una opción..."] + list(item.title() for item in template_desplegables.template.keys()))

# If a dropdown option is selected, show the different forms
if selected_table != "Selecciona una opción...":
    selection = fetch_all(selected_table) # {'Gerente': 1, 'Subgerentes': 2}
    df = pd.DataFrame(selection.keys(), columns=["Opciones disponibles:"])

    # Edit options
    with st.form("edit_options", clear_on_submit=True):
        st.header(f"Editar opciones para {selected_table}")

        edit = st.dataframe(
            df,
            use_container_width=True, 
            hide_index=True, 
            key="edit_data", 
            on_select="rerun", 
            selection_mode="single-row"
        )

        new_option = st.text_input(f"Escribe el nuevo nombre de la opción:", value="")

        edit_option_button = st.form_submit_button("Editar opción", type="primary")

        if edit_option_button:
            # Get the selected row indices
            selected_indices = edit.selection["rows"]

            if selected_indices:
                # Get the actual option value from the DataFrame
                selected_option = df.iloc[selected_indices[0]].iloc[0]

                # Try to edit the option
                result_edit = edit_options(selected_table.lower(), selected_option, new_option.title())

                if result_edit["success"]:
                    st.session_state.data_refresh_counter += 1
                    st.success(result_edit["message"])
                else:
                    st.error(result_edit["message"])

            else:
                st.warning("Por favor selecciona una opción para editar.")
            time.sleep(2)
            st.rerun()

    # Add option
    with st.form("add_option", clear_on_submit=True):
        st.header(f"Agregar una opción a {selected_table}	")
        new_option = st.text_input(f"Agregar nueva opción a {selected_table}", value="")
        add_option_button = st.form_submit_button("Añadir opción", type="primary")

        if add_option_button:
            # Add new option to database
            result_add = add_option(selected_table.lower(), new_option.title())

            if result_add["success"]:
                st.session_state.data_refresh_counter += 1
                st.success(result_add["message"])
            else:
                st.error(result_add["message"])

            time.sleep(2)
            st.rerun()

    # Delete option
    with st.form("delete_option", clear_on_submit=True):
        st.header(f"Eliminar una opción de {selected_table}")
        st.write("**Nota:** Si la opción está en uso en el plan, no podrás eliminarla, solo podrás editarla.")

        delete = st.dataframe(
            df,
            use_container_width=True, 
            hide_index=True, 
            key="delete_data", 
            on_select="rerun", 
            selection_mode="single-row"
        )

        delete_option_button = st.form_submit_button("Eliminar opción", type="primary")

        if delete_option_button:
            # Get the selected row indices
            selected_indices = delete.selection["rows"]

            if selected_indices:
                # Get the actual option value from the DataFrame
                selected_option = df.iloc[selected_indices[0]].iloc[0]

                # Try to delete the option
                result_delete = delete_option(selected_table.lower(), selected_option)

                if result_delete["success"]:
                    st.session_state.data_refresh_counter += 1
                    st.success(result_delete["message"])
                else:
                    st.error(result_delete["message"])

            else:
                st.warning("Por favor selecciona una opción para eliminar.")
            time.sleep(2)
            st.rerun()
