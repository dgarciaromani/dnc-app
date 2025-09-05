import requests
import shutil
import sqlite3
from src.data import template_desplegables

DB_PATH = "database.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def fill_database_from_template():
    """Populate all lookup tables from template_desplegables.py."""
    conn = get_connection()
    cur = conn.cursor()

    try:
        for table, values in template_desplegables.template.items():
            for item in values:
                cur.execute(f"""INSERT OR IGNORE INTO {table} (name) VALUES (?)""", (item,))
        conn.commit()

    finally:
        conn.close()


def download_demo_db():
    FILE_ID = "1n4Hl2PX_0rKjdd8jBTS2Y4fjJ0eoc0yR"
    url = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(DB_PATH, "wb") as f:
            shutil.copyfileobj(response.raw, f)
        return True
    else:
        return False


def fetch_plan():
    query = """
    SELECT 
        fp.id, 
        o.name AS "Origen",
        g.name AS "Gerencia", 
        sg.name AS "Subgerencia",
        a.name AS "Área", 
        d.name AS "Desafío Estratégico", 
        fp.actividad_formativa AS "Actividad Formativa", 
        fp.objetivo_desempeno AS "Objetivo Desempeño", 
        fp.contenidos_especificos AS "Contenidos", 
        fp.skills AS "Skills", 
        fp.keywords AS "Keywords",
        au.name AS "Audiencia", 
        m.name AS "Modalidad",
        f.name AS "Fuente",
        fp.fuente_interna AS "Fuente Interna",
        p.name AS "Prioridad", 
        fp.created_at AS "Fecha Creación",
        GROUP_CONCAT(lc.linkedin_course, ', ') AS "Curso Sugerido LinkedIn"
    FROM final_plan fp
    LEFT JOIN origin o ON fp.origin_id = o.id
    LEFT JOIN gerencias g ON fp.gerencia_id = g.id
    LEFT JOIN subgerencias sg ON fp.subgerencia_id = sg.id
    LEFT JOIN areas a ON fp.area_id = a.id
    LEFT JOIN desafios d ON fp.desafio_id = d.id
    LEFT JOIN audiencias au ON fp.audiencia_id = au.id
    LEFT JOIN modalidades m ON fp.modalidad_id = m.id
    LEFT JOIN fuentes f ON fp.fuente_id = f.id
    LEFT JOIN prioridades p ON fp.prioridad_id = p.id
    LEFT JOIN plan_linkedin_courses plc ON plc.plan_id = fp.id
    LEFT JOIN linkedin_courses lc ON lc.id = plc.course_id
    GROUP BY fp.id
    ORDER BY g.name;
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_final_plan(gerencia_id, subgerencia_id, area_id, desafio_id, actividad, objetivo, contenidos, skills, keywords, modalidad_id, fuente_id, fuente_interna, audiencia_id, prioridad_id, plan_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE final_plan
        SET gerencia_id = ?,
            subgerencia_id = ?,
            area_id = ?,
            desafio_id = ?,
            actividad_formativa = ?,
            objetivo_desempeno = ?,
            contenidos_especificos = ?,
            skills = ?,
            keywords = ?,
            modalidad_id = ?,
            fuente_id = ?,
            fuente_interna = ?,
            audiencia_id = ?,
            prioridad_id = ?,
            last_updated = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            gerencia_id,
            subgerencia_id,
            area_id,
            desafio_id,
            actividad,
            objetivo,
            contenidos,
            skills,
            keywords,
            modalidad_id,
            fuente_id,
            fuente_interna,
            audiencia_id,
            prioridad_id,
            plan_id
        )
    )
    conn.commit()
    conn.close()


def update_plan_linkedin_courses(plan_id, linkedin_course_name):
    """Update LinkedIn courses for a specific plan"""
    conn = get_connection()
    cur = conn.cursor()

    # First, remove existing LinkedIn course relationships for this plan
    cur.execute("DELETE FROM plan_linkedin_courses WHERE plan_id = ?", (plan_id,))

    # If a LinkedIn course is specified, add the relationship
    if linkedin_course_name and linkedin_course_name.strip():
        # Find the LinkedIn course ID by name
        cur.execute("SELECT id FROM linkedin_courses WHERE linkedin_course = ?", (linkedin_course_name.strip(),))
        course_row = cur.fetchone()

        if course_row:
            course_id = course_row[0]
            cur.execute(
                "INSERT INTO plan_linkedin_courses (plan_id, course_id) VALUES (?, ?)",
                (plan_id, course_id)
            )

    conn.commit()
    conn.close()


def delete_plan_entry(plan_id):
    """Delete a plan entry and its related LinkedIn courses"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT plan_id FROM plan_linkedin_courses WHERE plan_id = ?", (plan_id,))
        relationships_found = cur.fetchone()

        if relationships_found:
            # First delete the LinkedIn course relationships
            cur.execute("DELETE FROM plan_linkedin_courses WHERE plan_id = ?", (plan_id,))

        # Then delete the plan entry
        cur.execute("DELETE FROM final_plan WHERE id = ?", (plan_id,))

        conn.commit()

        # Return True if the main plan entry was deleted (regardless of LinkedIn courses)
        return True

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def fetch_all(table):
    """Fetch all rows from a table as a dict {'name': id}"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if table == "linkedin_courses":
        cur.execute(f"SELECT id, linkedin_course AS name FROM linkedin_courses")
    else:
        cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    conn.close()
    return {name: id for id, name in rows}


def update_respondents(name, email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO respondents (nombre, email) 
        VALUES (?, ?)
        """,
        (
            name, 
            email
        )
    )
    conn.commit()
    conn.close()
    return cur.lastrowid


def update_raw_data_forms(submission_id, origin, gerencia_id, subgerencia_id, area_id, desafio_id, cambios, que_falta, aprendizajes, audiencia_id, modalidad_id, fuente_id, fuente_interna, prioridad_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM origin WHERE name = ?", (origin,))
    origin_id = cur.fetchone()[0]
    cur.execute(
        """
        INSERT INTO raw_data_forms (submission_id, origin_id, gerencia_id, subgerencia_id, area_id, desafio_id, cambios, que_falta, aprendizajes, audiencia_id, modalidad_id, fuente_id, fuente_interna, prioridad_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            submission_id,
            origin_id,
            gerencia_id,
            subgerencia_id,
            area_id,
            desafio_id,
            cambios,
            que_falta,
            aprendizajes,
            audiencia_id,
            modalidad_id,
            fuente_id,
            fuente_interna,
            prioridad_id
        )
    )
    conn.commit()
    conn.close()


def insert_row_into_plan(data, origin, gerencia_id, subgerencia_id, area_id, desafio_id, modalidad_id, audiencia_id, fuente_id, fuente_interna, prioridad_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM origin WHERE name = ?", (origin,))
    origin_id = cur.fetchone()[0]
    cur.execute(
        """
        INSERT INTO final_plan (
            origin_id,
            gerencia_id,
            subgerencia_id,
            area_id,
            desafio_id,
            actividad_formativa,
            objetivo_desempeno,
            contenidos_especificos,
            skills,
            keywords,
            modalidad_id,
            fuente_id,
            fuente_interna,
            audiencia_id,
            prioridad_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            origin_id,
            gerencia_id, 
            subgerencia_id, 
            area_id, 
            desafio_id, 
            data.get("Actividad formativa"),
            data.get("Objetivo de desempeño"),
            data.get("Contenidos específicos"),
            data.get("Skills"),
            data.get("Keywords"),
            modalidad_id,
            fuente_id,
            fuente_interna,
            audiencia_id, 
            prioridad_id
        )
    )
    conn.commit()
    conn.close()

def get_virtual_courses():
    query = """
    SELECT 
        fp.id AS id,
        GROUP_CONCAT(lc.linkedin_course, ', ') AS "Estado Curso",
        g.name AS "Gerencia",
        fp.actividad_formativa AS "Actividad Formativa", 
        fp.objetivo_desempeno AS "Objetivo Desempeño", 
        fp.contenidos_especificos AS "Contenidos", 
        fp.skills AS "Skills", 
        fp.keywords AS "Keywords",
        au.name AS "Audiencia", 
        p.name AS "Prioridad"
    FROM final_plan fp
    LEFT JOIN gerencias g ON fp.gerencia_id = g.id
    LEFT JOIN audiencias au ON fp.audiencia_id = au.id
    LEFT JOIN modalidades m ON fp.modalidad_id = m.id
    LEFT JOIN fuentes f ON fp.fuente_id = f.id
    LEFT JOIN prioridades p ON fp.prioridad_id = p.id
    LEFT JOIN plan_linkedin_courses plc ON plc.plan_id = fp.id
    LEFT JOIN linkedin_courses lc ON lc.id = plc.course_id
    WHERE m.name = 'Virtual' AND f.name = 'Externa'
    GROUP BY fp.id
    ORDER BY fp.actividad_formativa;
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_linkedin_course(selection, plan_id):
    conn = get_connection()
    cur = conn.cursor()

    # First, remove any existing LinkedIn course associations for this plan
    cur.execute("DELETE FROM plan_linkedin_courses WHERE plan_id = ?", (int(plan_id),))

    # Insert the LinkedIn course if it doesn't exist
    cur.execute("""
        INSERT OR IGNORE INTO linkedin_courses (
                linkedin_urn,
                linkedin_course,
                linkedin_url)
        VALUES (?, ?, ?)
    """,
    (selection['URN'],
     selection['Title'],
     selection['URL'])
    )

    conn.commit()

    # Get the course ID
    cur.execute("""
        SELECT id FROM linkedin_courses
        WHERE linkedin_urn = ? AND linkedin_course = ? AND linkedin_url = ?
    """,
    (selection['URN'],
     selection['Title'],
     selection['URL']))

    course_id = cur.fetchone()["id"]

    # Insert the association (this will now be the only one for this plan)
    cur.execute("""
        INSERT INTO plan_linkedin_courses (
                plan_id,
                course_id)
        VALUES (?, ?)
    """,
    (int(plan_id),
     course_id)
    )

    conn.commit()
    conn.close()

def get_respondents():
    query = """
    SELECT
        r.nombre AS "Nombre",
        r.email AS "Correo",
        g.name AS "Gerencia",
        sg.name AS "Subgerencia",
        a.name AS "Área",
        COUNT(d.submission_id) AS "N Necesidades Levantadas"
    FROM respondents r
        LEFT JOIN raw_data_forms d ON r.id = d.submission_id
        LEFT JOIN gerencias g ON d.gerencia_id = g.id
        LEFT JOIN subgerencias sg ON d.subgerencia_id = sg.id
        LEFT JOIN areas a ON d.area_id = a.id
    GROUP BY r.id, r.nombre, r.email, g.name, sg.name, a.name
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_linkedin_courses():
    query = """
    SELECT
        lc.id AS "id",
        lc.linkedin_course AS "Nombre del Curso",
        lc.linkedin_url AS "URL",
        lc.linkedin_urn AS "URN",
        GROUP_CONCAT(fp.actividad_formativa, '; ') AS "Actividades Formativas Asociadas",
        COUNT(plc.plan_id) AS "Número de Actividades Asociadas"
    FROM linkedin_courses lc
    LEFT JOIN plan_linkedin_courses plc ON lc.id = plc.course_id
    LEFT JOIN final_plan fp ON plc.plan_id = fp.id
    GROUP BY lc.id, lc.linkedin_course, lc.linkedin_urn, lc.linkedin_url
    ORDER BY lc.linkedin_course
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_raw_data_forms():
    query = """
    SELECT
        o.name AS "Origen",
        r.nombre AS "Levantado por",
        des.name AS "Desafío Estratégico",
        d.cambios AS "Qué Debe Ocurrir",
        d.que_falta AS "Qué Falta",
        d.aprendizajes as "Aprendizajes",
        au.name AS "Audiencia",
        f.name AS "Fuente",
        p.name AS "Prioridad",
        d.created_at AS "Fecha Creación"
    FROM respondents r
        JOIN raw_data_forms d ON r.id = d.submission_id
        JOIN origin o ON d.origin_id = o.id
        JOIN desafios des ON d.desafio_id = des.id
        JOIN audiencias au ON d.audiencia_id = au.id
        JOIN fuentes f ON d.fuente_id = f.id
        JOIN prioridades p ON d.prioridad_id = p.id
    ORDER BY d.created_at DESC
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def edit_options(selected_table, old_value, new_value):
    """Update an option name in the specified table"""
    if not old_value or not new_value or old_value == new_value:
        return {"success": False, "message": "Invalid or unchanged values"}
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check if new value already exists (case-insensitive)
        cur.execute(f"SELECT * FROM {selected_table}")
        options = cur.fetchall()

        for option in options:
            if new_value.lower() == option["name"].lower() and old_value.lower() != option["name"].lower():
                return {"success": False, "message": f"'{new_value}' ya existe como opción."}
        
        # Update the option
        cur.execute(f"UPDATE {selected_table} SET name = ? WHERE name = ?", 
                   (new_value, old_value))
        
        if cur.rowcount > 0:
            conn.commit()
            return {"success": True, "message": f"'{old_value}' ha sido cambiado a '{new_value}'"}
        else:
            return {"success": False, "message": f"'{old_value}' no fue encontrado."}
            
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error en la base de datos: {str(e)}"}
    finally:
        conn.close()


def add_option(selected_table, new_option):
    # Check if the option is empty
    if not new_option or not new_option.strip():
        return {"success": False, "message": "La opción no puede estar vacía.", "id": None}

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Check if the option is already in the table (check in lowercase)
        cur.execute(f"SELECT * FROM {selected_table}")
        options = cur.fetchall()

        for option in options:
            if new_option.lower() == option["name"].lower():
                return {"success": False, "message": f"'{new_option}' ya existe como opción.", "id": None}
        
        # Use INSERT OR IGNORE to handle duplicates gracefully if the option is not in the table
        cur.execute(f"INSERT OR IGNORE INTO {selected_table} (name) VALUES (?)", (new_option.strip(),))

        if cur.rowcount > 0:
            # Get the ID of the inserted row
            option_id = cur.lastrowid
            conn.commit()
            return {"success": True, "message": f"'{new_option}' fue agregada correctamente.", "id": option_id}
        else:
            # Row was not inserted (already exists)
            conn.rollback()
            return {"success": False, "message": f"'{new_option}' ya existe como opción.", "id": None}

    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error en la base de datos: {str(e)}", "id": None}
    finally:
        conn.close()


def delete_option(selected_table, option_to_delete):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Mapping from table names to their corresponding column names in final_plan
        column_mapping = {
            'gerencias': 'gerencia_id',
            'subgerencias': 'subgerencia_id',
            'areas': 'area_id',
            'desafios': 'desafio_id',
            'audiencias': 'audiencia_id',
            'modalidades': 'modalidad_id',
            'fuentes': 'fuente_id',
            'prioridades': 'prioridad_id'
        }

        # Get the correct column name
        if selected_table not in column_mapping:
            return {"success": False, "message": f"Tabla '{selected_table}' no es válida para eliminación."}

        column_name = column_mapping[selected_table]

        # Check if the option is currently in use by any final_plan records
        cur.execute(f"""
            SELECT 1
            FROM final_plan fp
            INNER JOIN {selected_table} t ON fp.{column_name} = t.id
            WHERE t.name = ?
            LIMIT 1""", (option_to_delete,))

        # If any records found, the option is being used
        if cur.fetchone():
            return {"success": False, "message": f"'{option_to_delete}' está siendo usada en la base de datos, por lo que no puede ser eliminada."}
        else:
            # Safe deletion with parameter binding
            cur.execute(f"DELETE FROM {selected_table} WHERE name = ?", (option_to_delete,))
            conn.commit()
            return {"success": True, "message": f"'{option_to_delete}' fue eliminada correctamente."}

    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error en la base de datos: {str(e)}", "id": None}
    finally:
        conn.close()


def get_plan_metrics(origin_filter=None, gerencia_filter=None, subgerencia_filter=None,
                     area_filter=None, desafio_filter=None, audiencia_filter=None,
                     modalidad_filter=None, fuente_filter=None, prioridad_filter=None,
                     asociaciones_filter=None):
    """Get summary metrics, optionally filtered by various criteria"""
    conn = get_connection()

    try:
        # Build WHERE conditions for final_plan table
        where_conditions = []
        params = []

        # Origin filter
        if origin_filter and origin_filter != "Todos":
            origin_id_query = "SELECT id FROM origin WHERE name = ?"
            origin_id = conn.execute(origin_id_query, (origin_filter,)).fetchone()
            if origin_id:
                where_conditions.append("fp.origin_id = ?")
                params.append(origin_id[0])
            else:
                return {"activities": 0, "linkedin": 0}

        # Gerencia filter
        if gerencia_filter:
            gerencia_ids = []
            for gerencia in gerencia_filter:
                gerencia_id_query = "SELECT id FROM gerencias WHERE name = ?"
                gerencia_id = conn.execute(gerencia_id_query, (gerencia,)).fetchone()
                if gerencia_id:
                    gerencia_ids.append(str(gerencia_id[0]))
            if gerencia_ids:
                where_conditions.append(f"fp.gerencia_id IN ({', '.join(gerencia_ids)})")

        # Subgerencia filter
        if subgerencia_filter:
            subgerencia_ids = []
            for subgerencia in subgerencia_filter:
                subgerencia_id_query = "SELECT id FROM subgerencias WHERE name = ?"
                subgerencia_id = conn.execute(subgerencia_id_query, (subgerencia,)).fetchone()
                if subgerencia_id:
                    subgerencia_ids.append(str(subgerencia_id[0]))
            if subgerencia_ids:
                where_conditions.append(f"fp.subgerencia_id IN ({', '.join(subgerencia_ids)})")

        # Área filter
        if area_filter:
            area_ids = []
            for area in area_filter:
                area_id_query = "SELECT id FROM areas WHERE name = ?"
                area_id = conn.execute(area_id_query, (area,)).fetchone()
                if area_id:
                    area_ids.append(str(area_id[0]))
            if area_ids:
                where_conditions.append(f"fp.area_id IN ({', '.join(area_ids)})")

        # Desafío filter
        if desafio_filter:
            desafio_ids = []
            for desafio in desafio_filter:
                desafio_id_query = "SELECT id FROM desafios WHERE name = ?"
                desafio_id = conn.execute(desafio_id_query, (desafio,)).fetchone()
                if desafio_id:
                    desafio_ids.append(str(desafio_id[0]))
            if desafio_ids:
                where_conditions.append(f"fp.desafio_id IN ({', '.join(desafio_ids)})")

        # Audiencia filter
        if audiencia_filter:
            audiencia_ids = []
            for audiencia in audiencia_filter:
                audiencia_id_query = "SELECT id FROM audiencias WHERE name = ?"
                audiencia_id = conn.execute(audiencia_id_query, (audiencia,)).fetchone()
                if audiencia_id:
                    audiencia_ids.append(str(audiencia_id[0]))
            if audiencia_ids:
                where_conditions.append(f"fp.audiencia_id IN ({', '.join(audiencia_ids)})")

        # Modalidad filter
        if modalidad_filter:
            modalidad_ids = []
            for modalidad in modalidad_filter:
                modalidad_id_query = "SELECT id FROM modalidades WHERE name = ?"
                modalidad_id = conn.execute(modalidad_id_query, (modalidad,)).fetchone()
                if modalidad_id:
                    modalidad_ids.append(str(modalidad_id[0]))
            if modalidad_ids:
                where_conditions.append(f"fp.modalidad_id IN ({', '.join(modalidad_ids)})")

        # Fuente filter
        if fuente_filter:
            fuente_ids = []
            for fuente in fuente_filter:
                fuente_id_query = "SELECT id FROM fuentes WHERE name = ?"
                fuente_id = conn.execute(fuente_id_query, (fuente,)).fetchone()
                if fuente_id:
                    fuente_ids.append(str(fuente_id[0]))
            if fuente_ids:
                where_conditions.append(f"fp.fuente_id IN ({', '.join(fuente_ids)})")

        # Prioridad filter
        if prioridad_filter:
            prioridad_ids = []
            for prioridad in prioridad_filter:
                prioridad_id_query = "SELECT id FROM prioridades WHERE name = ?"
                prioridad_id = conn.execute(prioridad_id_query, (prioridad,)).fetchone()
                if prioridad_id:
                    prioridad_ids.append(str(prioridad_id[0]))
            if prioridad_ids:
                where_conditions.append(f"fp.prioridad_id IN ({', '.join(prioridad_ids)})")

        # Build WHERE clause
        where_clause = " AND ".join(where_conditions) if where_conditions else ""

        # Build activities query with asociaciones filter
        activities_where = where_clause
        if asociaciones_filter:
            if "Con cursos asociados" in asociaciones_filter and "Sin cursos asociados" in asociaciones_filter:
                # Both selected - no additional filter
                pass
            elif "Con cursos asociados" in asociaciones_filter:
                # Only activities with LinkedIn courses
                if activities_where:
                    activities_where = f"{activities_where} AND fp.id IN (SELECT DISTINCT plc.plan_id FROM plan_linkedin_courses plc)"
                else:
                    activities_where = "fp.id IN (SELECT DISTINCT plc.plan_id FROM plan_linkedin_courses plc)"
            elif "Sin cursos asociados" in asociaciones_filter:
                # Only activities without LinkedIn courses
                if activities_where:
                    activities_where = f"{activities_where} AND fp.id NOT IN (SELECT DISTINCT plc.plan_id FROM plan_linkedin_courses plc)"
                else:
                    activities_where = "fp.id NOT IN (SELECT DISTINCT plc.plan_id FROM plan_linkedin_courses plc)"

        if activities_where:
            activities_query = f"SELECT COUNT(*) FROM final_plan fp WHERE {activities_where}"
        else:
            activities_query = "SELECT COUNT(*) FROM final_plan"

        # Build LinkedIn courses query with asociaciones filter
        if asociaciones_filter:
            if "Con cursos asociados" in asociaciones_filter and "Sin cursos asociados" in asociaciones_filter:
                # Both selected - no additional filter
                linkedin_where = where_clause
            elif "Con cursos asociados" in asociaciones_filter:
                # Only with LinkedIn courses
                if where_clause:
                    linkedin_where = f"{where_clause} AND plc.course_id IS NOT NULL"
                else:
                    linkedin_where = "plc.course_id IS NOT NULL"
            elif "Sin cursos asociados" in asociaciones_filter:
                # Only without LinkedIn courses
                if where_clause:
                    linkedin_where = f"{where_clause} AND plc.course_id IS NULL"
                else:
                    linkedin_where = "plc.course_id IS NULL"
            else:
                linkedin_where = where_clause
        else:
            linkedin_where = where_clause

        if linkedin_where:
            linkedin_query = f"""
                SELECT COUNT(DISTINCT lc.id)
                FROM linkedin_courses lc
                LEFT JOIN plan_linkedin_courses plc ON lc.id = plc.course_id
                LEFT JOIN final_plan fp ON plc.plan_id = fp.id
                WHERE {linkedin_where}
            """
        else:
            linkedin_query = "SELECT COUNT(*) FROM linkedin_courses"

        # Execute queries
        activities = conn.execute(activities_query, params).fetchone()[0] if params else conn.execute(activities_query).fetchone()[0]
        linkedin = conn.execute(linkedin_query, params).fetchone()[0] if params and linkedin_where else conn.execute(linkedin_query).fetchone()[0]

        return {
            "activities": activities,
            "linkedin": linkedin
        }

    finally:
        conn.close()