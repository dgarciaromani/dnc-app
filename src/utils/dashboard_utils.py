import pandas as pd
import altair as alt


def create_pie_chart(data, title, color_scheme='category20'):
    """Create a clean pie chart with legend (simpler and more reliable)"""
    if data.empty:
        return alt.Chart().mark_text(text="Sin datos", fontSize=20, color='gray')

    # Find the categorical column
    category_col = data.columns[0]

    # Calculate percentages
    total = data['count'].sum()
    data = data.copy()

    # Replace null values with "No especificado"
    data[category_col] = data[category_col].fillna("No especificado")

    data['percentage'] = (data['count'] / total * 100).round(1)

    # Create pie chart with legend
    chart = alt.Chart(data).encode(
        theta=alt.Theta("count:Q"),
        color=alt.Color(f"{category_col}:N", scale=alt.Scale(scheme=color_scheme), legend=alt.Legend(title=title.split(' ')[0])),
        tooltip=[f'{category_col}:N', 'count:Q', 'percentage:Q']
    ).mark_arc(
        outerRadius=80,
        innerRadius=0
    ).properties(
        title=title,
        width=280,
        height=280
    )

    return chart


def create_horizontal_bar_chart(data, title, color_scheme='category20'):
    """Create a horizontal bar chart - better for categorical data comparison"""
    if data.empty:
        return alt.Chart().mark_text(text="Sin datos", fontSize=20, color='gray')

    # Find the categorical column
    category_col = data.columns[0]

    # Calculate percentages
    total = data['count'].sum()
    data = data.copy()

    # Replace null values with "No especificado"
    data[category_col] = data[category_col].fillna("No especificado")

    data['percentage'] = (data['count'] / total * 100).round(1)

    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('count:Q', title='Cantidad', axis=alt.Axis(format='d')),
        y=alt.Y(f'{category_col}:N', title='', sort='-x'),
        color=alt.Color(f'{category_col}:N', scale=alt.Scale(scheme=color_scheme), legend=None),
        tooltip=[f'{category_col}:N', 'count:Q', 'percentage:Q']
    ).properties(
        title=title,
        width=400,
        height=300
    )

    return chart


def create_vertical_bar_chart(data, title, color_scheme='category20'):
    """Create a vertical bar chart - better for fewer categories"""
    if data.empty:
        return alt.Chart().mark_text(text="Sin datos", fontSize=20, color='gray')

    # Find the categorical column
    category_col = data.columns[0]

    # Calculate percentages
    total = data['count'].sum()
    data = data.copy()

    # Replace null values with "No especificado"
    data[category_col] = data[category_col].fillna("No especificado")

    data['percentage'] = (data['count'] / total * 100).round(1)

    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X(f'{category_col}:N', title='', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('count:Q', title='Cantidad'),
        color=alt.Color(f'{category_col}:N', scale=alt.Scale(scheme=color_scheme), legend=None),
        tooltip=[f'{category_col}:N', 'count:Q', 'percentage:Q']
    ).properties(
        title=title,
        width=400,
        height=300
    )

    return chart