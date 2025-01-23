import os
import streamlit as st
from together import Together
import json
from datetime import datetime, timedelta, time
from io import StringIO
from typing import Dict, List, Optional, Any


# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses Together's chat models to generate responses. "
    "To use this app, you need to provide an Together API key, which you can get from [api.together.xyz](https://api.together.xyz/settings/api-keys). "
)

DEBUG_PRINT = os.getenv('DEBUG_PRINT')
together_api_key = os.getenv('TOGETHER_API_KEY')

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
     
    dbg("Initializing download_messages()")        
    now = datetime.now()
    fn = f"chatbot7_messages_{now.strftime('%Y-%m-%d')}_{int(now.timestamp())}.json"
    st.session_state.messages_json = json.dumps(st.session_state.messages)
    dbg(f"st.session_state.messages_json now {len(st.session_state.messages_json)} bytes, {len(st.session_state.messages)} messages")
    st.markdown("Save chat messages by downloading\n(bug: click twice to get latest).")
    st.download_button(
        label="Download Messages as JSON",
        data=st.session_state.messages_json,
        on_click=lambda: dbg("Download button clicked"),
        file_name=fn,
        mime="application/json"
    )
    dbg(f"Initialized download_button {len(st.session_state.messages_json)} bytes for file_name={fn}")


# If this is a @st.fragment, then messages do not appear in chat window, need to manually add them
def upload_messages() -> None:
    """Handle file upload to restore previous chat messages from JSON file.
    
    Allows users to upload a previously saved chat history JSON file.
    Updates st.session_state.messages with the uploaded content if successful.
    Displays error message if JSON parsing fails or format is invalid.
    """
    dbg("Initializing upload_messages()")
    
    st.session_state.uploaded_file = st.file_uploader("Restore Saved Chat Messages.\nChoose a File", type="json")
    
    if st.session_state.uploaded_file is not None:
        try:
            dbg(f"Uploaded {st.session_state.uploaded_file.size} bytes from {st.session_state.uploaded_file.name}")
            stringio = StringIO(st.session_state.uploaded_file.getvalue().decode("utf-8"))
            string_data = stringio.read()
            messages = json.loads(string_data)
            
            # Validate uploaded messages format
            if not isinstance(messages, list):
                st.error("Uploaded JSON must contain a list of messages")
                return
            for msg in messages:
                if not isinstance(msg, dict) or not all(key in msg for key in ['role', 'content']):
                    st.error("Each message must be a dictionary with 'role' and 'content' keys")
                    return
            st.session_state.messages = messages
            dbg(f"Uploaded {len(st.session_state.messages)} messages {st.session_state.uploaded_file.size} bytes from {st.session_state.uploaded_file.name}")
            st.session_state.uploaded_file = None 
            dbg(f"Upload Complete")
            
        except Exception as e:
            st.error("Error parsing JSON file. Please ensure the file is in the correct format.", icon="🚨")
            st.exception(e)

def messages_append(m: Dict[str, str]) -> None:
    """Append a message to the session state messages.
    
    Args:
        m (Dict[str, str]): Message dictionary containing 'role' and 'content' keys.
            Will add 'dt' timestamp if not present.
    
    Raises:
        ValueError: If message dict is missing required keys or has invalid types
    """
    if not m:
        return
        
    if not isinstance(m, dict):
        raise ValueError("Message must be a dictionary")
        
    required_keys = ['role', 'content']
    if not all(key in m for key in required_keys):
        raise ValueError(f"Message missing required keys: {required_keys}")
        
    if not all(isinstance(m[key], str) for key in required_keys):
        raise ValueError("Message 'role' and 'content' must be strings")
        
    if "dt" not in m:
        m["dt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    
    st.session_state.messages.append(m)    
    dbg(f"Now have {len(st.session_state.messages)} messages")


# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    download_messages()
    upload_messages()

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message. This will display
# automatically at the bottom of the page.
if prompt := st.chat_input("What can I answer for you today?"):
    # Store and display the current prompt.
    dbg(f"user: {prompt}")
    messages_append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate a response 
    response = together.chat.completions.create(
        # model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],
        max_tokens=1024,
        temperature=0,
    )
    # Stream the response to the chat using `st.write_stream`, then store it in 
    # session state.
    with st.chat_message("assistant"):
        st.markdown(response.choices[0].message.content)
    dbg(f"assistant: received {len(response.choices[0].message.content)} characters")
    messages_append({"role": "assistant", "content": response.choices[0].message.content})




#TODO use langchain https://python.langchain.com/v0.1/docs/integrations/chat/together/
