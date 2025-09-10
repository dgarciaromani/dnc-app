import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()
c.execute("PRAGMA foreign_keys = ON;")

# =========================
# Selectbox tables
# =========================

# Gerencias
c.execute("""
CREATE TABLE IF NOT EXISTS gerencias (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
)
""")

# Subgerencias
c.execute("""
CREATE TABLE IF NOT EXISTS subgerencias (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
)
""")

# Areas
c.execute("""
CREATE TABLE IF NOT EXISTS areas (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
)
""")

# Desafios
c.execute("""
CREATE TABLE IF NOT EXISTS desafios (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
)
""")

# Audiencias
c.execute("""
CREATE TABLE IF NOT EXISTS audiencias (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
)
""")

# Modalidades
c.execute("""
CREATE TABLE IF NOT EXISTS modalidades (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
)
""")

# Fuentes
c.execute("""
CREATE TABLE IF NOT EXISTS fuentes (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
)
""")

# Prioridad
c.execute("""
CREATE TABLE IF NOT EXISTS prioridades (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
)
""")

# =========================
# Special tables
# =========================

c.execute("""
CREATE TABLE IF NOT EXISTS origin (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
)
""")

# =========================
# Main tables - DNC
# =========================

# User information
c.execute("""
CREATE TABLE IF NOT EXISTS respondents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    email TEXT
)
""")

# Raw form submissions
c.execute("""
CREATE TABLE IF NOT EXISTS raw_data_forms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL,
    origin_id INTEGER,
    gerencia_id INTEGER,
    subgerencia_id INTEGER,
    area_id INTEGER,
    desafio_id INTEGER,
    cambios TEXT,
    que_falta TEXT,
    aprendizajes TEXT,
    audiencia_id INTEGER,
    modalidad_id INTEGER,
    fuente_id INTEGER,
    fuente_interna TEXT,
    prioridad_id INTEGER,         
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES respondents(id),
    FOREIGN KEY (origin_id) REFERENCES origin(id),
    FOREIGN KEY (gerencia_id) REFERENCES gerencias(id),
    FOREIGN KEY (subgerencia_id) REFERENCES subgerencias(id),
    FOREIGN KEY (area_id) REFERENCES areas(id),
    FOREIGN KEY (desafio_id) REFERENCES desafios(id),
    FOREIGN KEY (audiencia_id) REFERENCES audiencias(id),
    FOREIGN KEY (modalidad_id) REFERENCES modalidades(id),
    FOREIGN KEY (prioridad_id) REFERENCES prioridades(id)
)
""")

# Output from AI (plan)
c.execute("""
CREATE TABLE IF NOT EXISTS final_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origin_id INTEGER,
    gerencia_id INTEGER,
    subgerencia_id INTEGER,
    area_id INTEGER,
    desafio_id INTEGER,
    actividad_formativa TEXT,
    objetivo_desempeno TEXT,
    contenidos_especificos TEXT,
    skills TEXT,
    keywords TEXT,
    modalidad_id INTEGER,
    fuente_id INTEGER,
    fuente_interna TEXT,
    audiencia_id INTEGER,
    prioridad_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    
    FOREIGN KEY (origin_id) REFERENCES origin(id),
    FOREIGN KEY (gerencia_id) REFERENCES gerencias(id),
    FOREIGN KEY (subgerencia_id) REFERENCES subgerencias(id),
    FOREIGN KEY (area_id) REFERENCES areas(id),
    FOREIGN KEY (desafio_id) REFERENCES desafios(id),
    FOREIGN KEY (modalidad_id) REFERENCES modalidades(id),
    FOREIGN KEY (audiencia_id) REFERENCES audiencias(id),
    FOREIGN KEY (prioridad_id) REFERENCES prioridades(id)
)
""")

# Linkedin courses
c.execute("""
CREATE TABLE IF NOT EXISTS linkedin_courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    linkedin_urn TEXT,
    linkedin_course TEXT,
    linkedin_url TEXT,
    UNIQUE(linkedin_urn, linkedin_course, linkedin_url)
)
""")

# Join table for final_plan and LinkedIn courses
c.execute("""
CREATE TABLE IF NOT EXISTS plan_linkedin_courses (
    plan_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    PRIMARY KEY (plan_id, course_id),
    FOREIGN KEY (plan_id) REFERENCES final_plan(id),
    FOREIGN KEY (course_id) REFERENCES linkedin_courses(id)
)
""")

conn.commit()
conn.close()