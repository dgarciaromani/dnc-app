import streamlit as st
import requests
import math

def get_access_token():
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "client_credentials",
        "client_id": st.secrets["CLIENT_ID_LINKEDIN"],
        "client_secret": st.secrets["CLIENT_SECRET_LINKEDIN"]
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]


def fetch_courses(keywords, asset_type, count_per_page, results_spanish, level, options_level):
    """Fetch all courses with pagination and return clean data."""
    
    # Build the request URL
    base_url = "https://api.linkedin.com/v2/learningAssets"
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "q": "criteria",
        "assetFilteringCriteria.keyword": keywords,
        "assetFilteringCriteria.assetTypes[0]": asset_type,
        "fields": "urn, title, details",
        "start": 0,
        "count": count_per_page
    }

    if results_spanish:
        params["assetFilteringCriteria.locales[0].language"] = "es"

    if level != "ALL":
        params["assetFilteringCriteria.difficultyLevels[0]"] = level    

    # Make the request
    response = requests.get(base_url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    # Check if there are any courses found
    total = data.get("paging", {}).get("total", 0)

    if total == 0:
        return [], 0

    # Prepare to collect all courses
    all_courses = []

    # Calculate how many pages
    pages = math.ceil(total / count_per_page)

    print("Fetching LinkedIn Learning courses...") # DEBUG

    for page in range(pages):
        start = page * count_per_page
        params["start"] = start

        print(f"Fetching page {page+1}/{pages} (start={start})...") # DEBUG
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Create a dict mapping for fast lookup
        level_map = dict(options_level)

        for element in data.get("elements", []):
            urn = element.get("urn")
            title = element.get("title", {}).get("value")
            details = element.get("details", {})
            level = details.get("level")
            duration_seconds = details.get('timeToComplete', {}).get('duration')
            description = details.get('description', {}).get('value')
            #short_description = details.get('shortDescription', {}).get('value')

            # Map level with fallback
            level_label = level_map.get(level, "Nivel no especificado")

            course = {
                "Title": title,
                "Level": level_label,
                'Duration (min)': round(duration_seconds / 60) if duration_seconds else "Información no disponible",
                "Description": description if description else "Descripción no disponible",
                #"Short Description": short_description if short_description else "Descripción corta no disponible",
                "URL": details.get("urls", {}).get("webLaunch"),
                "URN": urn
            }
            all_courses.append(course)

    print(f"{total} LinkedIn Learning courses fetched successfully.") # DEBUG
    return all_courses, total


def search_course_by_identifier(identifier):
    """Search for a specific LinkedIn course by URN using the correct API endpoints."""
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        if identifier.startswith("urn:li:"):
            url = f"https://api.linkedin.com/v2/learningAssets/{identifier}"
            params = {
                "fields": "urn,title,details",
                "expandDepth": 2  # Include full details
            }

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            course_data = response.json()

            # Process single course response
            urn = course_data.get("urn")
            title = course_data.get("title", {}).get("value")
            details = course_data.get("details", {})

            if not title:
                return None, f"Curso no encontrado o no accesible: {identifier}"

            level = details.get("level")
            duration_info = details.get('timeToComplete', {})
            duration_seconds = duration_info.get('duration') if duration_info else None
            description = details.get('description', {}).get('value')
            url = details.get("urls", {}).get("webLaunch")

            course = {
                "Title": title,
                "Level": level,
                'Duration (min)': round(duration_seconds / 60) if duration_seconds else "Información no disponible",
                "Description": description if description else "Descripción no disponible",
                "URL": url,
                "URN": urn
            }
            return course, None

        else:
            return None, "Por favor, ingresa un URN válido (urn:li:...)."

    except requests.RequestException as e:
        error_msg = str(e)
        if "404" in error_msg:
            return None, f"Curso no encontrado: {identifier}"
        elif "403" in error_msg:
            return None, f"Acceso denegado. El curso puede no estar disponible: {identifier}"
        else:
            return None, f"Error de API: {error_msg}"

