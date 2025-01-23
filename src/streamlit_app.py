import os
import streamlit as st
from together import Together
import json
from datetime import datetime, timedelta, time
from io import StringIO
from typing import Dict, List, Optional, Any
from services.chat_model import ChatModelService
from services.chat_history import ChatHistoryManager
from dotenv import load_dotenv 

load_dotenv() 
DEBUG_PRINT = os.getenv('DEBUG_PRINT')
together_api_key = os.getenv('TOGETHER_API_KEY')


# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses Together's chat models to generate responses. "
    "To use this app, you need to provide an Together API key, which you can get from [api.together.xyz](https://api.together.xyz/settings/api-keys). "
)

def dbg(msg):
    if DEBUG_PRINT:
        print(f"{datetime.now().strftime('%H:%M:%S.%f')} {msg}", flush=True)

dbg(f"DEBUG_PRINT set to {DEBUG_PRINT}")

if  together_api_key:
    st.write("Using TOGETHER_API_KEY from env variable")
else:
    # Ask user for their OpenAI API key via `st.text_input`.
    # Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
    # via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
    together_api_key = st.text_input("Together API Key", type="password")
    if not together_api_key:
        st.info("Please add your Together API key to continue.", icon="🗝️")
        st.stop()

together = Together(api_key=together_api_key)

# Initialize services
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatHistoryManager()

if together_api_key:
    chat_model = ChatModelService(together_api_key)
    
@st.fragment
def download_messages() -> None:
    """Create a download button to save chat messages as JSON file.
    
    Note:
        Currently requires clicking twice to get latest messages due to 
        Streamlit limitations with deferred data updates.
    """
    #TODO - should not have to click twice to get latest json, but we do for now.
    #TODO - Revisit once "Deferred data" is out, see roadmap.streamlit.app 
    # https://github.com/streamlit/streamlit/issues/5053
    # https://discuss.streamlit.io/t/generating-a-report-and-performing-download-on-download-button-click/53095/2
    #
    dbg("Initializing download_messages()")        
    now = datetime.now()
    fn = f"chatbot7_messages_{now.strftime('%Y-%m-%d')}_{int(now.timestamp())}.json"
    messages_json = st.session_state.chat_history.export_json()
    dbg(f"messages_json now {len(messages_json)} bytes, {len(st.session_state.chat_history.messages)} messages")
    st.markdown("Save chat messages by downloading.  \nClick twice to get latest (bug).")
    st.download_button(
        label="Download Messages as JSON",
        data=messages_json,
        on_click=lambda: dbg("Download button clicked"),
        file_name=fn,
        mime="application/json"
    )
    dbg(f"Initialized download_button {len(messages_json)} bytes for file_name={fn}")

# Update upload_messages()
def upload_messages() -> None:
    """Handle file upload to restore previous chat messages from JSON file.
    
    Allows users to upload a previously saved chat history JSON file.
    Updates st.session_state.messages with the uploaded content if successful.
    Displays error message if JSON parsing fails or format is invalid.
    """
    dbg("Initializing upload_messages()")
    uploaded_file = st.file_uploader("Restore Saved Chat Messages.\nChoose a File", type="json")    
    if uploaded_file is not None:
        try:
            dbg(f"Uploaded {uploaded_file.size} bytes from {uploaded_file.name}")
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            string_data = stringio.read()
            st.session_state.chat_history.import_json(string_data)
            uploaded_file = None
        except Exception as e:
            st.error("Error parsing JSON file. Please ensure the file is in the correct format.", icon="🚨")
            st.exception(e)

with st.sidebar:
    download_messages()
    upload_messages()

# Update chat display and input handling
for message in st.session_state.chat_history.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What can I answer for you today?"):
    message = {"role": "user", "content": prompt}
    st.session_state.chat_history.append_message(message)
    
    with st.chat_message("user"):
        st.markdown(prompt)

    response = chat_model.generate_response(st.session_state.chat_history.messages)
    
    with st.chat_message("assistant"):
        st.markdown(response)
        
    st.session_state.chat_history.append_message({
        "role": "assistant",
        "content": response
    })




