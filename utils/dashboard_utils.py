import pandas as pd
import altair as alt
from utils.database_utils import get_connection

def create_donut_chart(data, title, color_scheme='category20'):
    """Create a donut chart with percentages"""
    if data.empty:
        return alt.Chart().mark_text(text="Sin datos", fontSize=20, color='gray')

    # Find the categorical column (it could be 'gerencia', 'name', 'category', etc.)
    categorical_cols = ['gerencia', 'name', 'category']
    category_col = None
    for col in categorical_cols:
        if col in data.columns:
            category_col = col
            break

    # If no standard categorical column found, use the first non-numeric column
    if category_col is None:
        for col in data.columns:
            if col != 'count' and data[col].dtype == 'object':
                category_col = col
                break

    if category_col is None:
        # Fallback to first column if nothing else works
        category_col = data.columns[0]

    # Calculate percentages
    total = data['count'].sum()
    data = data.copy()
    data['percentage'] = (data['count'] / total * 100).round(1)
    data['label'] = data.apply(lambda row: f"{row[category_col]}: {row['percentage']}%", axis=1)

    base = alt.Chart(data).encode(
        theta=alt.Theta("count:Q"),
        color=alt.Color(f"{category_col}:N", scale=alt.Scale(scheme=color_scheme)),
        tooltip=[f'{category_col}:N', 'count:Q', 'percentage:Q']
    )

    pie = base.mark_arc(innerRadius=20, outerRadius=80)

    text = base.mark_text(radius=50, size=12).encode(
        text="percentage:Q",
        color=alt.value("white")
    )

    return (pie + text).properties(
        title=title,
        width=400,
        height=400
    )

def get_dashboard_data():
    """Get all data needed for the dashboard"""
    conn = get_connection()

    # Respondents data
    respondents_query = """
    SELECT
        g.name AS gerencia,
        COUNT(DISTINCT r.id) AS count
    FROM respondents r
    LEFT JOIN raw_data_forms d ON r.id = d.submission_id
    LEFT JOIN gerencias g ON d.gerencia_id = g.id
    WHERE g.name IS NOT NULL
    GROUP BY g.name
    ORDER BY count DESC
    """
    respondents_by_gerencia = pd.read_sql_query(respondents_query, conn)

    # Needs by priority
    priority_query = """
    SELECT
        p.name AS category,
        COUNT(*) AS count
    FROM raw_data_forms d
    JOIN prioridades p ON d.prioridad_id = p.id
    GROUP BY p.name
    ORDER BY count DESC
    """
    needs_by_priority = pd.read_sql_query(priority_query, conn)

    # Needs by audience
    audience_query = """
    SELECT
        au.name AS category,
        COUNT(*) AS count
    FROM raw_data_forms d
    JOIN audiencias au ON d.audiencia_id = au.id
    GROUP BY au.name
    ORDER BY count DESC
    """
    needs_by_audience = pd.read_sql_query(audience_query, conn)

    # Needs by strategic challenge
    challenge_query = """
    SELECT
        des.name AS category,
        COUNT(*) AS count
    FROM raw_data_forms d
    JOIN desafios des ON d.desafio_id = des.id
    GROUP BY des.name
    ORDER BY count DESC
    """
    needs_by_challenge = pd.read_sql_query(challenge_query, conn)

    # Training activities by modality
    modality_query = """
    SELECT
        m.name AS category,
        COUNT(*) AS count
    FROM final_plan fp
    JOIN modalidades m ON fp.modalidad_id = m.id
    GROUP BY m.name
    ORDER BY count DESC
    """
    activities_by_modality = pd.read_sql_query(modality_query, conn)

    # Training activities by priority
    priority_plan_query = """
    SELECT
        p.name AS category,
        COUNT(*) AS count
    FROM final_plan fp
    JOIN prioridades p ON fp.prioridad_id = p.id
    GROUP BY p.name
    ORDER BY count DESC
    """
    activities_by_priority = pd.read_sql_query(priority_plan_query, conn)

    # Training activities by audience
    audience_plan_query = """
    SELECT
        au.name AS category,
        COUNT(*) AS count
    FROM final_plan fp
    JOIN audiencias au ON fp.audiencia_id = au.id
    GROUP BY au.name
    ORDER BY count DESC
    """
    activities_by_audience = pd.read_sql_query(audience_plan_query, conn)

    # LinkedIn courses usage
    linkedin_query = """
    SELECT
        CASE
            WHEN plc.course_id IS NOT NULL THEN 'Con Curso Asociado'
            ELSE 'Sin Curso Asociado'
        END AS category,
        COUNT(*) AS count
    FROM final_plan fp
    LEFT JOIN plan_linkedin_courses plc ON fp.id = plc.plan_id
    GROUP BY category
    """
    linkedin_usage = pd.read_sql_query(linkedin_query, conn)

    # Time-based trends
    time_query = """
    SELECT
        DATE(created_at) AS date,
        COUNT(*) AS submissions
    FROM raw_data_forms
    GROUP BY DATE(created_at)
    ORDER BY date
    """
    time_trends = pd.read_sql_query(time_query, conn)

    conn.close()

    return {
        'respondents_by_gerencia': respondents_by_gerencia,
        'needs_by_priority': needs_by_priority,
        'needs_by_audience': needs_by_audience,
        'needs_by_challenge': needs_by_challenge,
        'activities_by_modality': activities_by_modality,
        'activities_by_priority': activities_by_priority,
        'activities_by_audience': activities_by_audience,
        'linkedin_usage': linkedin_usage,
        'time_trends': time_trends
    }
