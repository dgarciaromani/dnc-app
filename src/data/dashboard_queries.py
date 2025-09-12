import pandas as pd
from src.data.database_utils import get_connection


def get_origin_filtered_data(origin_name=None):
    """Get dashboard data filtered by specific origin"""
    conn = get_connection()

    # If no origin filter, return all data
    if origin_name is None or origin_name == "Todos":
        return get_dashboard_data()

    try:
        # Get origin ID
        origin_query = "SELECT id FROM origin WHERE name = ?"
        origin_id = conn.execute(origin_query, (origin_name,)).fetchone()
        if not origin_id:
            return get_dashboard_data()  # Return all data if origin not found

        origin_id = origin_id[0]

        # Origin distribution
        origin_query = """
        SELECT
            o.name AS Origen,
            COUNT(*) AS count
        FROM final_matrix fm
        JOIN origin o ON fm.origin_id = o.id
        GROUP BY o.name
        ORDER BY count DESC
        """
        origin_of_needs = pd.read_sql_query(origin_query, conn)

        # Gerencias data - filter by origin (from final_matrix)
        gerencias_query = f"""
        SELECT
            g.name AS Gerencia,
            COUNT(*) AS count
        FROM final_matrix fm
        LEFT JOIN gerencias g ON fm.gerencia_id = g.id
        WHERE fm.origin_id = {origin_id}
        GROUP BY g.name
        ORDER BY count DESC
        """
        activities_by_gerencia = pd.read_sql_query(gerencias_query, conn)

        # Activities by subgerencia - filter by origin (from final_matrix)
        subgerencias_query = f"""
        SELECT
            sg.name AS Subgerencia,
            COUNT(*) AS count
        FROM final_matrix fm
        LEFT JOIN subgerencias sg ON fm.subgerencia_id = sg.id
        WHERE fm.origin_id = {origin_id}
        GROUP BY sg.name
        ORDER BY count DESC
        """
        activities_by_subgerencia = pd.read_sql_query(subgerencias_query, conn)

        # Activities by area - filter by origin (from final_matrix)
        areas_query = f"""
        SELECT
            a.name AS Área,
            COUNT(*) AS count
        FROM final_matrix fm
        LEFT JOIN areas a ON fm.area_id = a.id
        WHERE fm.origin_id = {origin_id}
        GROUP BY a.name
        ORDER BY count DESC
        """
        activities_by_area = pd.read_sql_query(areas_query, conn)

        # Activities by audience - filter by origin (from final_matrix)
        audience_query = f"""
        SELECT
            au.name AS Audiencia,
            COUNT(*) AS count
        FROM final_matrix fm
        JOIN audiencias au ON fm.audiencia_id = au.id
        WHERE fm.origin_id = {origin_id}
        GROUP BY au.name
        ORDER BY count DESC
        """
        activities_by_audience = pd.read_sql_query(audience_query, conn)

        # Activities by strategic challenge - filter by origin (from final_matrix)
        challenge_query = f"""
        SELECT
            des.name AS 'Desafío Estratégico',
            COUNT(*) AS count
        FROM final_matrix fm
        JOIN desafios des ON fm.desafio_id = des.id
        WHERE fm.origin_id = {origin_id}
        GROUP BY des.name
        ORDER BY count DESC
        """
        activities_by_challenge = pd.read_sql_query(challenge_query, conn)

        # Activities by priority - filter by origin (from final_matrix)
        priority_query = f"""
        SELECT
            p.name AS Prioridad,
            COUNT(*) AS count
        FROM final_matrix fm
        JOIN prioridades p ON fm.prioridad_id = p.id
        WHERE fm.origin_id = {origin_id}
        GROUP BY p.name
        ORDER BY count DESC
        """
        activities_by_priority = pd.read_sql_query(priority_query, conn)

        # Activities by modality - filter by origin (from final_matrix)
        modality_query = f"""
        SELECT
            m.name AS Modalidad,
            COUNT(*) AS count
        FROM final_matrix fm
        JOIN modalidades m ON fm.modalidad_id = m.id
        WHERE fm.origin_id = {origin_id}
        GROUP BY m.name
        ORDER BY count DESC
        """
        activities_by_modality = pd.read_sql_query(modality_query, conn)

        # Activities by source - filter by origin (from final_matrix)
        source_query = f"""
        SELECT
            f.name AS Fuente,
            COUNT(*) AS count
        FROM final_matrix fm
        JOIN fuentes f ON fm.fuente_id = f.id
        WHERE fm.origin_id = {origin_id}
        GROUP BY f.name
        ORDER BY count DESC
        """
        activities_by_source = pd.read_sql_query(source_query, conn)

        # LinkedIn courses usage - filter by origin
        linkedin_query = f"""
        SELECT
            CASE
                WHEN mlc.course_id IS NOT NULL THEN 'Con Curso Asociado'
                ELSE 'Sin Curso Asociado'
            END AS Actividades,
            COUNT(*) AS count
        FROM final_matrix fm
        LEFT JOIN matrix_linkedin_courses mlc ON fm.id = mlc.matrix_id
        WHERE fm.origin_id = {origin_id}
        GROUP BY Actividades
        """
        linkedin_usage = pd.read_sql_query(linkedin_query, conn)

        # Time-based trends - filter by origin 
        time_query = f"""
        SELECT
            DATE(created_at) AS Fecha,
            COUNT(*) AS Envíos
        FROM raw_data_forms
        WHERE origin_id = {origin_id}
        GROUP BY DATE(created_at)
        ORDER BY Fecha
        """
        time_trends = pd.read_sql_query(time_query, conn)

        # Monthly trends - filter by origin
        monthly_query = f"""
        SELECT
            strftime('%Y-%m', created_at) as Mes,
            COUNT(DISTINCT CASE WHEN submission_id IS NOT NULL THEN submission_id END) as Encuestados,
            COUNT(*) as Envíos
        FROM raw_data_forms
        WHERE origin_id = {origin_id}
        GROUP BY strftime('%Y-%m', created_at)
        ORDER BY Mes
        """
        monthly_trends = pd.read_sql_query(monthly_query, conn)

        return {
            'origin_of_needs': origin_of_needs,
            'activities_by_gerencia': activities_by_gerencia,
            'activities_by_subgerencia': activities_by_subgerencia,
            'activities_by_area': activities_by_area,
            'activities_by_audience': activities_by_audience,
            'activities_by_challenge': activities_by_challenge,
            'activities_by_priority': activities_by_priority,           
            'activities_by_modality': activities_by_modality,
            'activities_by_source': activities_by_source,
            'linkedin_usage': linkedin_usage,
            'time_trends': time_trends,
            'monthly_trends': monthly_trends
        }

    finally:
        conn.close()


def get_available_origins():
    """Get list of all available origins for filtering"""
    conn = get_connection()
    try:
        result = conn.execute("SELECT name FROM origin ORDER BY name").fetchall()
        return [row[0] for row in result]
    finally:
        conn.close()


def get_summary_metrics(origin_filter=None):
    """Get summary metrics, optionally filtered by origin"""
    conn = get_connection()

    try:
        if origin_filter is None or origin_filter == "Todos":
            # Get total counts (all from final_matrix for consistency)
            activities_query = "SELECT COUNT(*) FROM final_matrix"
            linkedin_query = "SELECT COUNT(*) FROM linkedin_courses"
            respondents_query = "SELECT COUNT(DISTINCT submission_id) FROM raw_data_forms"
            needs_query = "SELECT COUNT(*) FROM raw_data_forms"
        else:
            # Get origin ID
            origin_id_query = "SELECT id FROM origin WHERE name = ?"
            origin_id = conn.execute(origin_id_query, (origin_filter,)).fetchone()

            if not origin_id:
                return {"respondents": 0, "needs": 0, "activities": 0, "linkedin": 0}

            origin_id = origin_id[0]

            # Get filtered counts
            activities_query = f"SELECT COUNT(*) FROM final_matrix WHERE origin_id = {origin_id}"
            linkedin_query = f"""
                SELECT COUNT(*)
                FROM linkedin_courses lc
                LEFT JOIN matrix_linkedin_courses mlc ON lc.id = mlc.course_id
                LEFT JOIN final_matrix fm ON mlc.matrix_id = fm.id
                WHERE fm.origin_id = {origin_id}
            """
            needs_query = f"SELECT COUNT(*) FROM raw_data_forms"
            respondents_query = f"SELECT COUNT(DISTINCT submission_id) FROM raw_data_forms"

        respondents = conn.execute(respondents_query).fetchone()[0]
        needs = conn.execute(needs_query).fetchone()[0]
        activities = conn.execute(activities_query).fetchone()[0]
        linkedin = conn.execute(linkedin_query).fetchone()[0]

        # Get validation statistics
        if origin_filter is None or origin_filter == "Todos":
            validation_query = """
                SELECT
                    COUNT(CASE WHEN vm.validated = 1 THEN 1 END) as validated_count,
                    COUNT(CASE WHEN vm.validated = 0 OR vm.validated IS NULL THEN 1 END) as pending_count
                FROM final_matrix fm
                LEFT JOIN validated_matrix vm ON fm.id = vm.matrix_id
            """
        else:
            validation_query = f"""
                SELECT
                    COUNT(CASE WHEN vm.validated = 1 THEN 1 END) as validated_count,
                    COUNT(CASE WHEN vm.validated = 0 OR vm.validated IS NULL THEN 1 END) as pending_count
                FROM final_matrix fm
                LEFT JOIN validated_matrix vm ON fm.id = vm.matrix_id
                WHERE fm.origin_id = {origin_id}
            """

        validation_result = conn.execute(validation_query).fetchone()
        validated_count = validation_result[0] or 0
        pending_count = validation_result[1] or 0
        total_validation_activities = validated_count + pending_count
        validation_percentage = round((validated_count / total_validation_activities * 100), 1) if total_validation_activities > 0 else 0

        return {
            "respondents": respondents,
            "needs": needs,
            "activities": activities,
            "linkedin": linkedin,
            "validated_count": validated_count,
            "pending_count": pending_count,
            "total_validation_activities": total_validation_activities,
            "validation_percentage": validation_percentage
        }

    finally:
        conn.close()


def get_dashboard_data():
    """Get all data needed for the dashboard"""
    conn = get_connection()

    # Origin of needs in final matrix
    origin_query = """
    SELECT
        o.name AS Origen,
        COUNT(*) AS count
    FROM final_matrix fm
    JOIN origin o ON fm.origin_id = o.id
    GROUP BY o.name
    ORDER BY count DESC
    """
    origin_of_needs = pd.read_sql_query(origin_query, conn)

    # Activities by gerencia (from final_matrix)
    gerencias_query = """
    SELECT
        g.name AS Gerencia,
        COUNT(*) AS count
    FROM final_matrix fm
    LEFT JOIN gerencias g ON fm.gerencia_id = g.id
    WHERE g.name IS NOT NULL
    GROUP BY g.name
    ORDER BY count DESC
    """
    activities_by_gerencia = pd.read_sql_query(gerencias_query, conn)

    # Activities by subgerencia (from final_matrix)
    subgerencias_query = """
    SELECT
        sg.name AS Subgerencia,
        COUNT(*) AS count
    FROM final_matrix fm
    LEFT JOIN subgerencias sg ON fm.subgerencia_id = sg.id
    GROUP BY sg.name
    ORDER BY count DESC
    """
    activities_by_subgerencia = pd.read_sql_query(subgerencias_query, conn)

    # Activities by area (from final_matrix)
    areas_query = """
    SELECT
        a.name AS Área,
        COUNT(*) AS count
    FROM final_matrix fm
    LEFT JOIN areas a ON fm.area_id = a.id
    GROUP BY a.name
    ORDER BY count DESC
    """
    activities_by_area = pd.read_sql_query(areas_query, conn)

    # Activities by audience (from final_matrix)
    audience_query = """
    SELECT
        au.name AS Audiencia,
        COUNT(*) AS count
    FROM final_matrix fm
    JOIN audiencias au ON fm.audiencia_id = au.id
    GROUP BY au.name
    ORDER BY count DESC
    """
    activities_by_audience = pd.read_sql_query(audience_query, conn)

    # Activities by strategic challenge (from final_matrix)
    challenge_query = """
    SELECT
        des.name AS 'Desafío Estratégico',
        COUNT(*) AS count
    FROM final_matrix fm
    JOIN desafios des ON fm.desafio_id = des.id
    GROUP BY des.name
    ORDER BY count DESC
    """
    activities_by_challenge = pd.read_sql_query(challenge_query, conn)

    # Activities by priority (from final_matrix)
    priority_query = """
    SELECT
        p.name AS Prioridad,
        COUNT(*) AS count
    FROM final_matrix fm
    JOIN prioridades p ON fm.prioridad_id = p.id
    GROUP BY p.name
    ORDER BY count DESC
    """
    activities_by_priority = pd.read_sql_query(priority_query, conn)

    # Activities by modality (from final_matrix)
    modality_query = """
    SELECT
        m.name AS Modalidad,
        COUNT(*) AS count
    FROM final_matrix fm
    JOIN modalidades m ON fm.modalidad_id = m.id
    GROUP BY m.name
    ORDER BY count DESC
    """
    activities_by_modality = pd.read_sql_query(modality_query, conn)

    # Activities by source (from final_matrix)
    source_query = """
    SELECT
        f.name AS Fuente,
        COUNT(*) AS count
    FROM final_matrix fm
    JOIN fuentes f ON fm.fuente_id = f.id
    GROUP BY f.name
    ORDER BY count DESC
    """
    activities_by_source = pd.read_sql_query(source_query, conn)

    # LinkedIn courses usage
    linkedin_query = """
    SELECT
        CASE
            WHEN mlc.course_id IS NOT NULL THEN 'Con Curso Asociado'
            ELSE 'Sin Curso Asociado'
        END AS Actividades,
        COUNT(*) AS count
    FROM final_matrix fm
    LEFT JOIN matrix_linkedin_courses mlc ON fm.id = mlc.matrix_id
    GROUP BY Actividades
    """
    linkedin_usage = pd.read_sql_query(linkedin_query, conn)

    # Time-based trends (from final_matrix)
    time_query = """
    SELECT
        DATE(created_at) AS Fecha,
        COUNT(*) AS Envíos
    FROM raw_data_forms
    GROUP BY DATE(created_at)
    ORDER BY Fecha
    """
    time_trends = pd.read_sql_query(time_query, conn)
    
    # Monthly trends (from final_matrix)
    monthly_query = """
    SELECT
        strftime('%Y-%m', created_at) as Mes,
        COUNT(DISTINCT CASE WHEN submission_id IS NOT NULL THEN submission_id END) as Encuestados,
        COUNT(*) as Envíos
    FROM raw_data_forms
    GROUP BY strftime('%Y-%m', created_at)
    ORDER BY Mes
    """
    monthly_trends = pd.read_sql_query(monthly_query, conn)

    conn.close()

    return {
        'origin_of_needs': origin_of_needs,
        'activities_by_gerencia': activities_by_gerencia,
        'activities_by_subgerencia': activities_by_subgerencia,
        'activities_by_area': activities_by_area,
        'activities_by_audience': activities_by_audience,
        'activities_by_challenge': activities_by_challenge,
        'activities_by_priority': activities_by_priority,       
        'activities_by_modality': activities_by_modality,
        'activities_by_source': activities_by_source,
        'linkedin_usage': linkedin_usage,
        'time_trends': time_trends,
        'monthly_trends': monthly_trends
    }
