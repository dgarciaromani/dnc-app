import streamlit as st
from src.data.database_utils import delete_matrix_entry
import time

@st.dialog("🗑️ Confirmar Eliminación", width="large")
def show_delete_matrix_dialog(selected_rows_data, df):
    """Display delete confirmation dialog for selected matrix rows"""
    st.markdown("### 📋 Resumen de filas a eliminar:")

    # Display selected rows in a clean format
    selected_df = selected_rows_data[['Gerencia', 'Desafío Estratégico', 'Actividad Formativa', 'Audiencia']]
    st.dataframe(selected_df, use_container_width=True, hide_index=True)

    st.warning("⚠️ **ATENCIÓN:** Esta acción no se puede deshacer.")
    st.markdown(f"**Total de filas a eliminar:** {len(selected_rows_data)}")
    
    if st.button(f"🗑️ Confirmar Eliminación", type="primary", use_container_width=True):
        try:
            # Delete each selected row
            deleted_count = 0
            for _, row in selected_rows_data.iterrows():
                row_id = int(row['id'])
                delete_matrix_entry(row_id)
                deleted_count += 1

            st.success(f"✅ {deleted_count} fila(s) eliminada(s) correctamente.")
            time.sleep(2)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al eliminar las filas: {str(e)}")