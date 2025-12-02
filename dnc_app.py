import streamlit as st
import os
from src.data.database_utils import fill_database_from_template
from src.auth.authentication import hide_sidebar, authenticate_user, logout
from src.utils.clarity_utils import init_clarity

# Database initialization
if not os.path.exists("database.db"):
    # Database doesn't exist - recreate it
    try:
        import init_db
        fill_database_from_template()
    except ImportError:
        st.error("❌ La base de datos no pudo ser creada. Por favor, asegúrate de que todos los archivos estén correctamente cargados.")
        st.stop()
    except Exception as e:
        st.warning(f"⚠️ Error al inicializar la base de datos: {str(e)}")
        # Continue without stopping - allow app to run even with database issues
else:
    # Database exists, just ensure it's populated
    try:
        fill_database_from_template()
    except Exception as e:
        st.warning(f"⚠️ Error al verificar la base de datos: {str(e)}")
        # Continue without stopping - allow app to run even with database issues

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None

# Authentication check
if not st.session_state.authenticated:
    # Clean login page without navigation
    st.set_page_config(
        page_title="Módulo DNC - Login",
        page_icon="🔐",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    hide_sidebar()

    # Login page content
    st.title("🔐 Módulo DNC")
    # Login form
    with st.form("login_form"):
        username = st.text_input("Usuario", placeholder="Ingrese su nombre de usuario", key="login_username")
        password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña", key="login_password")

        # Center the submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_submitted = st.form_submit_button("Iniciar sesión", type="primary", use_container_width=True)

    # Process login when form is submitted
    if login_submitted:
        if username and password:
            user_info = authenticate_user(username, password)
            if user_info:
                # Set authentication state and redirect immediately
                st.session_state.authenticated = True
                st.session_state.username = user_info["username"]
                st.session_state.role = user_info["role"]
                st.session_state.name = user_info["name"]
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")
        else:
            st.warning("⚠️ Por favor, ingrese su nombre de usuario y contraseña")

    # Stop execution here - don't show anything else
    st.stop()

# User is logged in - show the main application with navigation
st.set_page_config(
    page_title="Módulo DNC",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Microsoft Clarity analytics (if project ID is configured)
# Only initialize once per session to avoid duplicate script tags
if "clarity_initialized" not in st.session_state:
    try:
        clarity_project_id = st.secrets.get("clarity_project_id", "")
        if clarity_project_id:
            init_clarity(clarity_project_id)
            st.session_state.clarity_initialized = True
    except (AttributeError, KeyError):
        # Secrets not configured or clarity_project_id not set - skip initialization
        st.session_state.clarity_initialized = True  # Mark as initialized to avoid retrying

# Show user info in sidebar
with st.sidebar:
    st.success(f"👤 Sesión iniciada como: {st.session_state.name}")

    # Logout button
    if st.button("🚪 Cerrar sesión", type="primary", use_container_width=True):
        logout()

# Define pages
dashboard = st.Page("pages/dashboard.py", title="Dashboard", icon=":material/dashboard:")
matrix = st.Page("pages/matriz_necesidades.py", title="Matriz de Necesidades", icon=":material/list:")
validation = st.Page("pages/validar_necesidades.py", title="Validar Necesidades", icon=":material/check_circle:")
dnc = st.Page("pages/cuestionario_dnc.py", title="Cuestionario DNC", icon=":material/question_answer:")
search_course = st.Page("pages/buscar_cursos.py", title="Buscar Cursos LinkedIn", icon=":material/search:")
respondents = st.Page("pages/encuestados.py", title="Encuestados", icon=":material/group:")
responses = st.Page("pages/respuestas.py", title="Respuestas", icon=":material/feedback:")
desplegables = st.Page("pages/desplegables.py", title="Administrar Desplegables", icon=":material/arrow_drop_down_circle:")
linkedin_courses = st.Page("pages/cursos_linkedin.py", title="Cursos LinkedIn", icon=":material/public:")
database = st.Page("pages/database.py", title="Base de Datos", icon=":material/database:")

# Role-based navigation
user_role = st.session_state.get("role", "user")

if user_role == "admin":
    # Admin sees all pages
    nav = st.navigation({
        "Home:": [dashboard],
        "Matriz de Necesidades:": [matrix, validation],
        "Levantar necesidades:": [dnc, respondents, responses],
        "Cursos LinkedIn:": [linkedin_courses, search_course],
        "Administración:": [desplegables, database],
    })
else:
    # Regular user only sees cuestionario DNC
    nav = st.navigation({
        "Encuesta:": [dnc],
    })

# Run navigation
nav.run()
