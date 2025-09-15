import streamlit as st
import io
import pandas as pd
import re


def remove_emojis(text):
    """Remove emojis and other unwanted Unicode characters from text."""
    if not isinstance(text, str):
        return text

    # Remove emojis and various Unicode symbols
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002700-\U000027BF"  # dingbats
        "\U0001f926-\U0001f937"  # gestures
        "\U00010000-\U0010ffff"  # other unicode
        "\u2640-\u2642"  # gender symbols
        "\u2600-\u2B55"  # misc symbols
        "\u200d"  # zero width joiner
        "\u23cf"  # eject symbol
        "\u23e9"  # fast forward
        "\u231a"  # watch
        "\ufe0f"  # variation selector
        "\u3030"  # wavy dash
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text).strip()


def download_excel_data(df):
    excel_data, _ = generate_excel_data(df)
    return excel_data

    
def generate_excel_data(df):
    try:
        # Create Excel file in memory
        buffer = io.BytesIO()

        # Prepare dataframe for export (remove hidden columns if they exist)
        export_df = df.copy()

        # Remove 'id' column if it exists (typically hidden in display)
        if 'id' in export_df.columns:
            export_df = export_df.drop('id', axis=1)

        # Remove emojis from all string columns
        for col in export_df.select_dtypes(include=['object', 'string']).columns:
            export_df[col] = export_df[col].apply(lambda x: remove_emojis(x) if pd.notna(x) else x)

        # Try to use xlsxwriter first, fallback to openpyxl
        try:
            # Create Excel writer with xlsxwriter engine
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, sheet_name='Datos', index=False)

                # Get workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets['Datos']

                # Add some formatting
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })

                # Write headers with formatting
                for col_num, value in enumerate(export_df.columns.values):
                    worksheet.write(0, col_num, value, header_format)

                # Auto-adjust column widths
                for i, col in enumerate(export_df.columns):
                    column_len = max(export_df[col].astype(str).str.len().max(),
                                     len(col)) + 2
                    worksheet.set_column(i, i, min(column_len, 50))  # Max width 50

        except ImportError:
            # Fallback to openpyxl if xlsxwriter is not available
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                export_df.to_excel(writer, sheet_name='Datos', index=False)

        buffer.seek(0)
        row_count = len(df)
        return buffer.getvalue(), row_count

    except Exception as e:
        st.error(f"❌ Error al generar el archivo Excel: {str(e)}")
        return None, 0


def download_excel_button(df, filename="datos.xlsx", button_text_prefix="📥 Descargar"):
    excel_data, row_count = generate_excel_data(df)

    if excel_data:
        button_text = f"{button_text_prefix} ({row_count} fila{'s' if row_count != 1 else ''})"

        st.download_button(
            label=button_text,
            data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )