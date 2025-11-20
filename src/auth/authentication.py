import streamlit as st

# Function to authenticate user
def authenticate_user(username, password):
    # Remove trailing and leading spaces from username and password
    username = username.strip() if username else ""
    password = password.strip() if password else ""
    
    auth_config = st.secrets.get("auth", {})

    # Check admin credentials
    if username == auth_config.get("admin_username") and password == auth_config.get("admin_password"):
        return {"username": username, "role": "admin", "name": "Administrador"}

    # Check user credentials
    elif username == auth_config.get("user_username") and password == auth_config.get("user_password"):
        return {"username": username, "role": "user", "name": "Jefatura"}

    # Check testing credentials
    elif username == auth_config.get("tester_username") and password == auth_config.get("tester_password"):
        return {"username": username, "role": "admin", "name": "Tester"}

    return None


# Function to logout
def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()


# Hide the sidebar completely for login page
def hide_sidebar():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="stHeader"] {
            display: none;
        }
        .main .block-container {
            max-width: 500px;
            padding-top: 3rem;
        }
    </style>
    """, unsafe_allow_html=True)


def stay_authenticated(username, role, name):
    st.session_state.authenticated = True
    st.session_state.username = username
    st.session_state.role = role
    st.session_state.name = name
    return
