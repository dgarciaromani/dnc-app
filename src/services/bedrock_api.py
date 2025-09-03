import streamlit as st
import requests
import json
import re

def get_from_ai(prompt, contents):
    print("Sending request to AI...") # DEBUG
    url = st.secrets["url"]
    auth_token = st.secrets["auth_token"]
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }

     # Build the content dynamically: start with the fixed prompt, then add all contents
    content_list = [{"text": prompt}] + [{"text": c} for c in contents]

    payload = {
        "model": "us.deepseek.r1-v1:0",  # Change if needed
        "conversation": [
            {
                "content": content_list,
                "role": "user"
            }
        ]
    }

    # Make the request
    response = requests.post(url, headers=headers, json=payload) # data=json.dumps(payload)
    print("Response status code:", response.status_code)  # DEBUG
    return response


def process_response(response):
    """Process the AI response and return the JSON data."""
    print("Processing AI response...")  # DEBUG
    if response.status_code == 200:
        try:
            print("Response received successfully.")  # DEBUG
            # Convert raw response to a dict
            response_json = response.json()
            #print(f"Response: {response_json}")  # DEBUG

            # Extract the "response" field from the API response
            markdown_response = response_json["response"]

            # Extract the JSON block from markdown using regex
            match = re.search(r'```json\n(.*?)\n```', markdown_response, re.DOTALL)
            json_str = match.group(1) if match else None

            # Convert JSON string to Python list of dicts
            data = json.loads(json_str)

            return data

        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error processing AI response: {e}")  # DEBUG
            st.error("Se ha generado un error al procesar la respuesta de IA. Por favor inténtalo nuevamente.")
            return None
    else:
        print(f"AI error occurred: {response.status_code} - {response.text}")  # DEBUG
        st.error(f"Error de IA al obtener recomendaciones. Por favor inténtalo nuevamente.")
        return None
