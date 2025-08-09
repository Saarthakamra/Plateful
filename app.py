# app.py
import streamlit as st
import json
import time
import os
import re

import googlemaps
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# app title and page configuration
st.set_page_config(page_title="Plateful", page_icon="🍽️")
st.title("🍽️ Plateful - Food Distribution Agent")

# initialize session state for chat history and context
if "messages" not in st.session_state:
    st.session_state.messages = []
if "context" not in st.session_state:
    st.session_state.context = {}
if "cached_orgs" not in st.session_state:
    st.session_state.cached_orgs = []


# helper function to find nearby ngos
def find_recipients(location: str):
    """Searches for organizations using Google Places API."""
    try:
        api_key = st.secrets["connections"]["gcp"]["GOOGLE_API_KEY"]
        gmaps = googlemaps.Client(key=api_key)
        geocode_result = gmaps.geocode(location)
        if not geocode_result:
            return {"error": f"Could not find coordinates for '{location}'"}

        lat_lng = geocode_result[0]['geometry']['location']
        places_result = gmaps.places_nearby(
            location=lat_lng, radius=8000, keyword='food bank OR charity OR food donation'
        )

        detailed_recipients = []
        for place in places_result.get('results', [])[:5]:
            place_id = place.get('place_id')
            if not place_id: continue

            details = gmaps.place(
                place_id=place_id,
                fields=['name', 'vicinity', 'formatted_phone_number', 'website', 'rating']
            )
            place_details = details.get('result', {})
            detailed_recipients.append({
                "name": place_details.get('name', 'N/A'),
                "address": place_details.get('vicinity', 'N/A'),
                "phone": place_details.get('formatted_phone_number', 'Not available'),
                "website": place_details.get('website', 'Not available'),
            })

        return {"recipients": detailed_recipients} if detailed_recipients else {"message": "No organizations found."}
    except Exception as e:
        return {"api_error": True, "error": str(e)}


# helper function to log donation requests to google sheets
def log_donation_request(user_name, user_phone, organizations):
    """Logs a donation request to a Google Sheet using the best available credentials."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

        # use local service_account file if it exists, otherwise use streamlit secrets
        if os.path.exists("service_account.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
        else:
            creds_json = dict(st.secrets["connections"]["gcp"]["service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scopes=scope)

        client = gspread.authorize(creds)
        spreadsheet_id = st.secrets["connections"]["gcp"]["GOOGLE_SHEET_ID"]
        sheet = client.open_by_key(spreadsheet_id).sheet1

        timestamp = time.ctime()
        rows_to_add = []
        for org in organizations:
            rows_to_add.append(
                [user_name, user_phone, org.get('name', 'N/A'), org.get('phone', 'N/A'), org.get('website', 'N/A'),
                 timestamp])

        # add headers if the sheet is empty
        if not sheet.get_all_values():
            sheet.append_row(["Donor Name", "Donor Phone", "NGO Name", "NGO Phone", "NGO Website", "Timestamp"])

        if rows_to_add:
            sheet.append_rows(rows_to_add)

        return {"success": True, "message": "Request logged successfully!"}
    except Exception as e:
        return {"error": f"Could not write to sheet: {e}"}


# helper function to format the ngo data for display
def format_organizations(orgs_data):
    """Formats the organization data for display."""
    response = ""
    for i, org in enumerate(orgs_data, 1):
        response += f"**{i}. {org['name']}**\n\n"
        response += f"   - **Address**: {org.get('address', 'N/A')}\n\n"
        response += f"   - **Phone**: {org.get('phone', 'Not available')}\n\n"
        response += f"   - **Website**: {org.get('website', 'Not available')}\n\n"
    return response


# main chat logic handler
def process_message(user_message):
    """Processes user message and manages conversation state."""
    message_lower = user_message.lower().strip()
    context = st.session_state.context

    # state machine for conversation flow
    if context.get('awaiting_user_name'):
        context['user_name'] = user_message
        context['awaiting_user_name'] = False
        context['awaiting_user_phone'] = True
        return "Thank you. Now, what is your phone number?"

    if context.get('awaiting_user_phone'):
        context['user_phone'] = user_message

        with st.spinner("Logging your request to Google Sheets..."):
            log_result = log_donation_request(
                context.get('user_name'),
                context.get('user_phone'),
                st.session_state.cached_orgs
            )

        st.session_state.context = {} # reset context after logging
        return f"✅ {log_result['message']}" if log_result.get('success') else f"❌ Error: {log_result['error']}"

    if context.get('awaiting_log_confirmation'):
        if message_lower == 'yes':
            context['awaiting_log_confirmation'] = False
            context['awaiting_user_name'] = True
            return "Great! To proceed, please provide your name."
        else:
            st.session_state.context = {}
            return "Okay, I won't log this request. Is there anything else I can help you with?"

    # initial search handler
    if "find" in message_lower or "donate" in message_lower or "where can" in message_lower:
        location_match = re.search(r'in\s(.+)', user_message, re.IGNORECASE)
        if not location_match:
            return "I can help with that! Please tell me the city you're in, for example: 'I want to donate in Delhi'."

        location = location_match.group(1).strip()
        with st.spinner(f"Searching for organizations in {location}..."):
            result_data = find_recipients(location)

        if "recipients" in result_data and result_data["recipients"]:
            st.session_state.cached_orgs = result_data["recipients"]
            response = f"I found these organizations in {location}:\n\n"
            response += format_organizations(st.session_state.cached_orgs)
            response += "\n\n**Would you like me to log this request for you? (yes/no)**"
            context['awaiting_log_confirmation'] = True
            return response
        else:
            return f"I'm sorry, I couldn't find any organizations. Error: {result_data.get('error', 'Unknown issue')}"

    return "I can help you find food donation centers. Please tell me your city, like 'Where can I donate in Delhi?'"


# render chat history and handle new input
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = process_message(prompt)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})