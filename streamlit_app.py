import os
import streamlit as st
from together import Together
import json
from datetime import datetime, timedelta, time
from io import StringIO


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
        print(f"{datetime.now().strftime("%H:%M:%S")} {msg}", flush=True)

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
def fragment_download():
    dbg(f"Initializing fragment_download()")
    messages_append()
    # Create a download link
    #
    #TODO - should not have to clicke twice to get latest json.
    
    dbg(f"Initializing download_button()")
    st.download_button(
        label="Download Messages as JSON",
        data=st.session_state.messages_json,
        on_click=lambda: messages_append(),
        file_name=f"chatbot7_messages_{datetime.now().strftime("%Y-%m-%d")}.json",
        mime="application/json"
    )

@st.fragment
def fragment_upload():
    dbg(f"Initializing fragment_upload()")
    uploaded_file = st.file_uploader("Choose a file", type="json")
    if uploaded_file is not None:
        try:
            dbg(f"Uploaded {uploaded_file.size} bytes from {uploaded_file.name}")
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            string_data = stringio.read()
            st.session_state.messages = json.loads(string_data)
            #
            #TODO - messages should not be duplicated on the web page, but should appear when uploaded
            #for m in st.session_state.messages:
            #    with st.chat_message(m["role"]):
            #        st.markdown(m["content"])
            uploaded_file = None 
        except Exception as e:
            st.error("Error parsing JSON file. Please ensure the file is in the correct format.", icon="🚨")
            st.exception(e)

def messages_append(m=None):
    if m:
        if "dt" not in m:
            m["dt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
        st.session_state.messages.append(m)
    st.session_state.messages_json = json.dumps(st.session_state.messages)
    dbg(f"st.session_state.messages_json now {len(st.session_state.messages_json)} bytes, {len(st.session_state.messages)} messages")


# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages_json = json.dumps(st.session_state.messages)

fragment_download()
fragment_upload()

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


#TODO - create a HTML button / link that will download json of st.session_state.messages
# https://discuss.streamlit.io/t/from-a-list-dict-to-ready-to-download-file/66430
#TODO - create an input (form box) that will except json messages


#TODO use langchain https://python.langchain.com/v0.1/docs/integrations/chat/together/
