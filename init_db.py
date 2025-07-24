import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# Table 1: user information
c.execute("""
CREATE TABLE IF NOT EXISTS respondents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    email TEXT,
    nivel1 TEXT,
    nivel2 TEXT,
    nivel3 TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Table 2: raw form submissions
c.execute("""
CREATE TABLE IF NOT EXISTS raw_data_forms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER,
    desafio TEXT,
    cambios TEXT,
    que_falta TEXT,
    aprendizajes TEXT,
    audiencia TEXT,
    fuente TEXT,
    prioridad TEXT,         
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Table 3: availability
c.execute("""
CREATE TABLE IF NOT EXISTS availability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER,
    audiencia TEXT,
    disponiblidad TEXT,
    no_disponible TEXT,       
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Table 4: output from AI (plan)
c.execute("""
CREATE TABLE IF NOT EXISTS final_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gerencia TEXT,
    subgerencia TEXT,
    area TEXT,
    desafio_estrategico TEXT,
    actividad_formativa TEXT,
    objetivo_desempeno TEXT,
    contenidos_especificos TEXT,
    skills TEXT,
    keywords TEXT,
    modalidad_sugerida TEXT,
    audiencia TEXT,
    prioridad TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    linkedin_course TEXT,
    linkedin_url TEXT
)
""")

conn.commit()
conn.close()