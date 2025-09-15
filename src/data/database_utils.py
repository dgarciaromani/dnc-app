import requests
import shutil
import sqlite3
import os
import time
from src.data import template_desplegables

DB_PATH = "database.db"


def safe_remove_file(file_path, max_retries=3, delay=0.5):
    """Safely remove a file with retries to handle Windows file locking"""
    for attempt in range(max_retries):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except OSError as e:
            if attempt == max_retries - 1:  # Last attempt
                print(f"Warning: Could not remove {file_path}: {e}")
                return False
            time.sleep(delay)
    return False

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


def validate_database_schema(db_path):
    """Validate that the database has the correct schema structure"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Get all table names
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in cur.fetchall()}

        # Expected tables
        expected_tables = {
            'gerencias', 'subgerencias', 'areas', 'desafios', 'audiencias',
            'modalidades', 'fuentes', 'prioridades', 'origin', 'respondents',
            'raw_data_forms', 'final_matrix', 'linkedin_courses', 'matrix_linkedin_courses'
        }

        # Check if all expected tables exist
        missing_tables = expected_tables - existing_tables
        if missing_tables:
            return False, f"Missing tables: {', '.join(missing_tables)}"

        # Check table structures
        expected_schemas = {
            'gerencias': ['id INTEGER PRIMARY KEY', 'name TEXT UNIQUE NOT NULL'],
            'subgerencias': ['id INTEGER PRIMARY KEY', 'name TEXT UNIQUE NOT NULL'],
            'areas': ['id INTEGER PRIMARY KEY', 'name TEXT UNIQUE NOT NULL'],
            'desafios': ['id INTEGER PRIMARY KEY', 'name TEXT UNIQUE NOT NULL'],
            'audiencias': ['id INTEGER PRIMARY KEY', 'name TEXT UNIQUE NOT NULL'],
            'modalidades': ['id INTEGER PRIMARY KEY', 'name TEXT UNIQUE NOT NULL'],
            'fuentes': ['id INTEGER PRIMARY KEY', 'name TEXT UNIQUE NOT NULL'],
            'prioridades': ['id INTEGER PRIMARY KEY', 'name TEXT UNIQUE NOT NULL'],
            'origin': ['id INTEGER PRIMARY KEY', 'name TEXT UNIQUE NOT NULL'],
            'respondents': ['id INTEGER PRIMARY KEY AUTOINCREMENT', 'nombre TEXT', 'email TEXT'],
            'raw_data_forms': [
                'id INTEGER PRIMARY KEY AUTOINCREMENT', 'submission_id INTEGER NOT NULL',
                'origin_id INTEGER', 'gerencia_id INTEGER', 'subgerencia_id INTEGER',
                'area_id INTEGER', 'desafio_id INTEGER', 'cambios TEXT', 'que_falta TEXT',
                'aprendizajes TEXT', 'audiencia_id INTEGER', 'modalidad_id INTEGER',
                'fuente_id INTEGER', 'fuente_interna TEXT', 'prioridad_id INTEGER',
                'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            ],
            'final_matrix': [
                'id INTEGER PRIMARY KEY AUTOINCREMENT', 'origin_id INTEGER', 'gerencia_id INTEGER',
                'subgerencia_id INTEGER', 'area_id INTEGER', 'desafio_id INTEGER',
                'actividad_formativa TEXT', 'objetivo_desempeno TEXT', 'contenidos_especificos TEXT',
                'skills TEXT', 'keywords TEXT', 'modalidad_id INTEGER', 'fuente_id INTEGER',
                'fuente_interna TEXT', 'audiencia_id INTEGER', 'prioridad_id INTEGER',
                'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP', 'last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            ],
            'linkedin_courses': [
                'id INTEGER PRIMARY KEY AUTOINCREMENT', 'linkedin_urn TEXT', 'linkedin_course TEXT',
                'linkedin_url TEXT'
            ],
            'matrix_linkedin_courses': [
                'matrix_id INTEGER NOT NULL', 'course_id INTEGER NOT NULL'
            ]
        }

        for table, expected_columns in expected_schemas.items():
            # Get actual column info
            cur.execute(f"PRAGMA table_info({table})")
            actual_columns = [f"{row[1]} {row[2]}" for row in cur.fetchall()]

            # Compare columns (simplified - just check that expected columns exist)
            for expected_col in expected_columns:
                col_name = expected_col.split()[0].lower()
                if not any(col_name in actual_col.lower() for actual_col in actual_columns):
                    return False, f"Table '{table}' missing column similar to '{expected_col}'"

        # Note: Foreign keys are enabled at connection level, not stored in database file

        return True, "Database schema is valid"

    except Exception as e:
        return False, f"Error validating database: {str(e)}"
    finally:
        if conn:
            conn.close()


def download_demo_db():
    FILE_ID = "1n4Hl2PX_0rKjdd8jBTS2Y4fjJ0eoc0yR"
    url = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

    response = requests.get(url, stream=True)
    if response.status_code != 200:
        return False, f"Failed to download database: HTTP {response.status_code}"

    # Download to a temporary file first
    temp_db_path = DB_PATH + ".temp"
    try:
        with open(temp_db_path, "wb") as f:
            shutil.copyfileobj(response.raw, f)

        # Validate the downloaded database
        is_valid, validation_message = validate_database_schema(temp_db_path)
        if not is_valid:
            # Clean up temp file
            safe_remove_file(temp_db_path)
            return False, f"Downloaded database validation failed: {validation_message}"

        # If validation passes, replace the original database
        if os.path.exists(DB_PATH):
            safe_remove_file(DB_PATH)
        os.rename(temp_db_path, DB_PATH)

        return True, "Database downloaded and validated successfully"

    except Exception as e:
        # Clean up temp file if it exists
        safe_remove_file(temp_db_path)
        return False, f"Error during database download/validation: {str(e)}"


def fetch_matrix():
    query = """
    SELECT
        fm.id,
        o.name AS "Origen",
        CASE WHEN vm.validated = 1 THEN '✅ Validado' ELSE '❌ Pendiente' END AS "Validación",
        g.name AS "Gerencia",
        sg.name AS "Subgerencia",
        a.name AS "Área",
        d.name AS "Desafío Estratégico",
        fm.actividad_formativa AS "Actividad Formativa",
        fm.objetivo_desempeno AS "Objetivo Desempeño",
        fm.contenidos_especificos AS "Contenidos",
        fm.skills AS "Skills",
        fm.keywords AS "Keywords",
        au.name AS "Audiencia",
        m.name AS "Modalidad",
        f.name AS "Fuente",
        fm.fuente_interna AS "Fuente Interna",
        p.name AS "Prioridad",
        fm.created_at AS "Fecha Creación",
        GROUP_CONCAT(lc.linkedin_course, ', ') AS "Curso Sugerido LinkedIn"
    FROM final_matrix fm
    LEFT JOIN origin o ON fm.origin_id = o.id
    LEFT JOIN gerencias g ON fm.gerencia_id = g.id
    LEFT JOIN subgerencias sg ON fm.subgerencia_id = sg.id
    LEFT JOIN areas a ON fm.area_id = a.id
    LEFT JOIN desafios d ON fm.desafio_id = d.id
    LEFT JOIN audiencias au ON fm.audiencia_id = au.id
    LEFT JOIN modalidades m ON fm.modalidad_id = m.id
    LEFT JOIN fuentes f ON fm.fuente_id = f.id
    LEFT JOIN prioridades p ON fm.prioridad_id = p.id
    LEFT JOIN matrix_linkedin_courses mlc ON mlc.matrix_id = fm.id
    LEFT JOIN validated_matrix vm ON vm.matrix_id = fm.id
    LEFT JOIN linkedin_courses lc ON lc.id = mlc.course_id
    GROUP BY fm.id
    ORDER BY g.name;
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_final_matrix(gerencia_id, subgerencia_id, area_id, desafio_id, actividad, objetivo, contenidos, skills, keywords, modalidad_id, fuente_id, fuente_interna, audiencia_id, prioridad_id, matrix_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE final_matrix
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
            matrix_id
        )
    )
    conn.commit()
    conn.close()


def update_matrix_linkedin_courses(matrix_id, linkedin_course_name):
    """Update LinkedIn courses for a specific matrix row"""
    conn = get_connection()
    cur = conn.cursor()

    # First, remove existing LinkedIn course relationships for this matrix row
    cur.execute("DELETE FROM matrix_linkedin_courses WHERE matrix_id = ?", (matrix_id,))

    # If a LinkedIn course is specified, add the relationship
    if linkedin_course_name and linkedin_course_name.strip():
        # Find the LinkedIn course ID by name
        cur.execute("SELECT id FROM linkedin_courses WHERE linkedin_course = ?", (linkedin_course_name.strip(),))
        course_row = cur.fetchone()

        if course_row:
            course_id = course_row[0]
            cur.execute(
                "INSERT INTO matrix_linkedin_courses (matrix_id, course_id) VALUES (?, ?)",
                (matrix_id, course_id)
            )

    conn.commit()
    conn.close()


def validate_matrix_entry(matrix_id, validated_by=None, validation_notes=None):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Ensure matrix_id is an integer
        matrix_id = int(matrix_id)

        # Check if validation record exists
        cur.execute("SELECT id FROM validated_matrix WHERE matrix_id = ?", (matrix_id,))
        existing_record = cur.fetchone()

        if existing_record:
            # Update existing validation record
            cur.execute("""
                UPDATE validated_matrix
                SET validated = 1, validated_by = ?, validation_notes = ?, validated_at = CURRENT_TIMESTAMP
                WHERE matrix_id = ?
            """, (validated_by, validation_notes, matrix_id))
        else:
            # Insert new validation record
            cur.execute("""
                INSERT INTO validated_matrix (matrix_id, validated, validated_by, validation_notes)
                VALUES (?, 1, ?, ?)
            """, (matrix_id, validated_by, validation_notes))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def unvalidate_matrix_entry(matrix_id):
    """Remove validation from a matrix entry"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Ensure matrix_id is an integer
        matrix_id = int(matrix_id)
        cur.execute("DELETE FROM validated_matrix WHERE matrix_id = ?", (matrix_id,))
        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def delete_matrix_entry(matrix_id):
    """Delete a matrix entry and its related LinkedIn courses and validation records"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Check for LinkedIn course relationships
        cur.execute("SELECT matrix_id FROM matrix_linkedin_courses WHERE matrix_id = ?", (matrix_id,))
        relationships_found = cur.fetchone()

        if relationships_found:
            # First delete the LinkedIn course relationships
            cur.execute("DELETE FROM matrix_linkedin_courses WHERE matrix_id = ?", (matrix_id,))

        # Check for validation records
        cur.execute("SELECT id FROM validated_matrix WHERE matrix_id = ?", (matrix_id,))
        validation_found = cur.fetchone()

        if validation_found:
            # Delete the validation record
            cur.execute("DELETE FROM validated_matrix WHERE matrix_id = ?", (matrix_id,))

        # Then delete the matrix entry
        cur.execute("DELETE FROM final_matrix WHERE id = ?", (matrix_id,))

        conn.commit()

        # Return True if the main matrix entry was deleted
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


def insert_row_into_matrix(data, origin, gerencia_id, subgerencia_id, area_id, desafio_id, modalidad_id, audiencia_id, fuente_id, fuente_interna, prioridad_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM origin WHERE name = ?", (origin,))
    origin_id = cur.fetchone()[0]
    cur.execute(
        """
        INSERT INTO final_matrix (
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
        fm.id AS id,
        GROUP_CONCAT(lc.linkedin_course, ', ') AS "Estado Curso",
        g.name AS "Gerencia",
        fm.actividad_formativa AS "Actividad Formativa", 
        fm.objetivo_desempeno AS "Objetivo Desempeño", 
        fm.contenidos_especificos AS "Contenidos", 
        fm.skills AS "Skills", 
        fm.keywords AS "Keywords",
        au.name AS "Audiencia", 
        p.name AS "Prioridad"
    FROM final_matrix fm
    LEFT JOIN gerencias g ON fm.gerencia_id = g.id
    LEFT JOIN audiencias au ON fm.audiencia_id = au.id
    LEFT JOIN modalidades m ON fm.modalidad_id = m.id
    LEFT JOIN fuentes f ON fm.fuente_id = f.id
    LEFT JOIN prioridades p ON fm.prioridad_id = p.id
    LEFT JOIN matrix_linkedin_courses mlc ON mlc.matrix_id = fm.id
    LEFT JOIN linkedin_courses lc ON lc.id = mlc.course_id
    WHERE m.name = 'Virtual' AND f.name = 'Externa'
    GROUP BY fm.id
    ORDER BY fm.actividad_formativa;
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_linkedin_course(selection, matrix_id):
    conn = get_connection()
    cur = conn.cursor()

    # First, remove any existing LinkedIn course associations for this matrix row
    cur.execute("DELETE FROM matrix_linkedin_courses WHERE matrix_id = ?", (int(matrix_id),))

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

    # Insert the association (this will now be the only one for this matrix row)
    cur.execute("""
        INSERT INTO matrix_linkedin_courses (
                matrix_id,
                course_id)
        VALUES (?, ?)
    """,
    (int(matrix_id),
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
        GROUP_CONCAT(fm.actividad_formativa, '; ') AS "Actividades Formativas Asociadas",
        COUNT(mlc.matrix_id) AS "Número de Actividades Asociadas"
    FROM linkedin_courses lc
    LEFT JOIN matrix_linkedin_courses mlc ON lc.id = mlc.course_id
    LEFT JOIN final_matrix fm ON mlc.matrix_id = fm.id
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


def add_linkedin_course_manual(course_data, selected_activities=None):
    """Add a LinkedIn course manually with optional activity associations."""
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Insert the LinkedIn course if it doesn't exist
        cur.execute("""
            INSERT OR IGNORE INTO linkedin_courses (
                linkedin_urn,
                linkedin_course,
                linkedin_url)
            VALUES (?, ?, ?)
        """,
        (course_data['URN'],
         course_data['Title'],
         course_data['URL'])
        )

        # Get the course ID
        cur.execute("""
            SELECT id FROM linkedin_courses
            WHERE linkedin_urn = ? AND linkedin_course = ? AND linkedin_url = ?
        """,
        (course_data['URN'],
         course_data['Title'],
         course_data['URL']))

        course_result = cur.fetchone()
        if not course_result:
            conn.rollback()
            return {"success": False, "message": "Failed to retrieve course after insertion"}

        course_id = course_result["id"]

        # If activities were selected, associate them
        if selected_activities:
            for activity_id in selected_activities:
                cur.execute("""
                    INSERT OR IGNORE INTO matrix_linkedin_courses (
                        matrix_id,
                        course_id)
                    VALUES (?, ?)
                """,
                (int(activity_id), course_id))

        conn.commit()
        return {"success": True, "message": f"Course '{course_data['Title']}' added successfully", "course_id": course_id}

    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error adding course: {str(e)}"}
    finally:
        conn.close()


def get_learning_activities_for_association():
    """Get all learning activities from final_matrix for association with LinkedIn courses."""
    query = """
    SELECT
        fm.id,
        fm.actividad_formativa AS "Actividad Formativa",
        g.name AS "Gerencia",
        fm.objetivo_desempeno AS "Objetivo Desempeño",
        fm.skills AS "Skills",
        fm.keywords AS "Keywords",
        au.name AS "Audiencia",
        p.name AS "Prioridad"
    FROM final_matrix fm
    LEFT JOIN gerencias g ON fm.gerencia_id = g.id
    LEFT JOIN audiencias au ON fm.audiencia_id = au.id
    LEFT JOIN prioridades p ON fm.prioridad_id = p.id
    ORDER BY fm.actividad_formativa
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
        # Mapping from table names to their corresponding column names in final_matrix
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

        # Check if the option is currently in use by any final_matrix records
        cur.execute(f"""
            SELECT 1
            FROM final_matrix fm
            INNER JOIN {selected_table} t ON fm.{column_name} = t.id
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


def get_matrix_metrics(origin_filter=None, gerencia_filter=None, subgerencia_filter=None,
                     area_filter=None, desafio_filter=None, audiencia_filter=None,
                     modalidad_filter=None, fuente_filter=None, prioridad_filter=None,
                     asociaciones_filter=None, validacion_filter=None):
    """Get summary metrics, optionally filtered by various criteria"""
    conn = get_connection()

    try:
        # Build WHERE conditions for final_matrix table
        where_conditions = []
        params = []

        # Origin filter
        if origin_filter and origin_filter != "Todos":
            origin_id_query = "SELECT id FROM origin WHERE name = ?"
            origin_id = conn.execute(origin_id_query, (origin_filter,)).fetchone()
            if origin_id:
                where_conditions.append("fm.origin_id = ?")
                params.append(origin_id[0])
            else:
                return {"activities": 0, "linkedin": 0, "validated": 0}

        # Gerencia filter
        if gerencia_filter:
            gerencia_ids = []
            for gerencia in gerencia_filter:
                gerencia_id_query = "SELECT id FROM gerencias WHERE name = ?"
                gerencia_id = conn.execute(gerencia_id_query, (gerencia,)).fetchone()
                if gerencia_id:
                    gerencia_ids.append(str(gerencia_id[0]))
            if gerencia_ids:
                where_conditions.append(f"fm.gerencia_id IN ({', '.join(gerencia_ids)})")

        # Subgerencia filter
        if subgerencia_filter:
            subgerencia_ids = []
            for subgerencia in subgerencia_filter:
                subgerencia_id_query = "SELECT id FROM subgerencias WHERE name = ?"
                subgerencia_id = conn.execute(subgerencia_id_query, (subgerencia,)).fetchone()
                if subgerencia_id:
                    subgerencia_ids.append(str(subgerencia_id[0]))
            if subgerencia_ids:
                where_conditions.append(f"fm.subgerencia_id IN ({', '.join(subgerencia_ids)})")

        # Área filter
        if area_filter:
            area_ids = []
            for area in area_filter:
                area_id_query = "SELECT id FROM areas WHERE name = ?"
                area_id = conn.execute(area_id_query, (area,)).fetchone()
                if area_id:
                    area_ids.append(str(area_id[0]))
            if area_ids:
                where_conditions.append(f"fm.area_id IN ({', '.join(area_ids)})")

        # Desafío filter
        if desafio_filter:
            desafio_ids = []
            for desafio in desafio_filter:
                desafio_id_query = "SELECT id FROM desafios WHERE name = ?"
                desafio_id = conn.execute(desafio_id_query, (desafio,)).fetchone()
                if desafio_id:
                    desafio_ids.append(str(desafio_id[0]))
            if desafio_ids:
                where_conditions.append(f"fm.desafio_id IN ({', '.join(desafio_ids)})")

        # Audiencia filter
        if audiencia_filter:
            audiencia_ids = []
            for audiencia in audiencia_filter:
                audiencia_id_query = "SELECT id FROM audiencias WHERE name = ?"
                audiencia_id = conn.execute(audiencia_id_query, (audiencia,)).fetchone()
                if audiencia_id:
                    audiencia_ids.append(str(audiencia_id[0]))
            if audiencia_ids:
                where_conditions.append(f"fm.audiencia_id IN ({', '.join(audiencia_ids)})")

        # Modalidad filter
        if modalidad_filter:
            modalidad_ids = []
            for modalidad in modalidad_filter:
                modalidad_id_query = "SELECT id FROM modalidades WHERE name = ?"
                modalidad_id = conn.execute(modalidad_id_query, (modalidad,)).fetchone()
                if modalidad_id:
                    modalidad_ids.append(str(modalidad_id[0]))
            if modalidad_ids:
                where_conditions.append(f"fm.modalidad_id IN ({', '.join(modalidad_ids)})")

        # Fuente filter
        if fuente_filter:
            fuente_ids = []
            for fuente in fuente_filter:
                fuente_id_query = "SELECT id FROM fuentes WHERE name = ?"
                fuente_id = conn.execute(fuente_id_query, (fuente,)).fetchone()
                if fuente_id:
                    fuente_ids.append(str(fuente_id[0]))
            if fuente_ids:
                where_conditions.append(f"fm.fuente_id IN ({', '.join(fuente_ids)})")

        # Prioridad filter
        if prioridad_filter:
            prioridad_ids = []
            for prioridad in prioridad_filter:
                prioridad_id_query = "SELECT id FROM prioridades WHERE name = ?"
                prioridad_id = conn.execute(prioridad_id_query, (prioridad,)).fetchone()
                if prioridad_id:
                    prioridad_ids.append(str(prioridad_id[0]))
            if prioridad_ids:
                where_conditions.append(f"fm.prioridad_id IN ({', '.join(prioridad_ids)})")

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
                    activities_where = f"{activities_where} AND fm.id IN (SELECT DISTINCT mlc.matrix_id FROM matrix_linkedin_courses mlc)"
                else:
                    activities_where = "fm.id IN (SELECT DISTINCT mlc.matrix_id FROM matrix_linkedin_courses mlc)"
            elif "Sin cursos asociados" in asociaciones_filter:
                # Only activities without LinkedIn courses
                if activities_where:
                    activities_where = f"{activities_where} AND fm.id NOT IN (SELECT DISTINCT mlc.matrix_id FROM matrix_linkedin_courses mlc)"
                else:
                    activities_where = "fm.id NOT IN (SELECT DISTINCT mlc.matrix_id FROM matrix_linkedin_courses mlc)"

        # Validación filter
        if validacion_filter:
            if "✅ Validado" in validacion_filter and "❌ Pendiente" in validacion_filter:
                # Both selected - no additional filter
                pass
            elif "✅ Validado" in validacion_filter:
                # Only validated activities
                if activities_where:
                    activities_where = f"{activities_where} AND fm.id IN (SELECT vm.matrix_id FROM validated_matrix vm WHERE vm.validated = 1)"
                else:
                    activities_where = "fm.id IN (SELECT vm.matrix_id FROM validated_matrix vm WHERE vm.validated = 1)"
            elif "❌ Pendiente" in validacion_filter:
                # Only unvalidated activities (not in validated_matrix)
                if activities_where:
                    activities_where = f"{activities_where} AND fm.id NOT IN (SELECT vm.matrix_id FROM validated_matrix vm)"
                else:
                    activities_where = "fm.id NOT IN (SELECT vm.matrix_id FROM validated_matrix vm)"

        if activities_where:
            activities_query = f"SELECT COUNT(*) FROM final_matrix fm WHERE {activities_where}"
        else:
            activities_query = "SELECT COUNT(*) FROM final_matrix"

        # Build LinkedIn courses query - count courses associated with filtered activities
        linkedin_where = where_clause

        if linkedin_where:
            linkedin_query = f"""
                SELECT COUNT(DISTINCT lc.id)
                FROM linkedin_courses lc
                INNER JOIN matrix_linkedin_courses mlc ON lc.id = mlc.course_id
                INNER JOIN final_matrix fm ON mlc.matrix_id = fm.id
                WHERE {linkedin_where}
            """
        else:
            linkedin_query = """
                SELECT COUNT(DISTINCT lc.id)
                FROM linkedin_courses lc
                INNER JOIN matrix_linkedin_courses mlc ON lc.id = mlc.course_id
            """

        # Build validated activities query
        validated_where = where_clause
        if validated_where:
            validated_query = f"""
                SELECT COUNT(*)
                FROM final_matrix fm
                INNER JOIN validated_matrix vm ON fm.id = vm.matrix_id AND vm.validated = 1
                WHERE {validated_where}
            """
        else:
            validated_query = """
                SELECT COUNT(*)
                FROM final_matrix fm
                INNER JOIN validated_matrix vm ON fm.id = vm.matrix_id AND vm.validated = 1
            """

        # Execute queries
        activities = conn.execute(activities_query, params).fetchone()[0] if params else conn.execute(activities_query).fetchone()[0]
        linkedin = conn.execute(linkedin_query, params).fetchone()[0] if params and linkedin_where else conn.execute(linkedin_query).fetchone()[0]
        validated = conn.execute(validated_query, params).fetchone()[0] if params and validated_where else conn.execute(validated_query).fetchone()[0]

        return {
            "activities": activities,
            "linkedin": linkedin,
            "validated": validated
        }

    finally:
        conn.close()