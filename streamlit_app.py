import streamlit as st
from together import Together

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses Together's chat models to generate responses. "
    "To use this app, you need to provide an Together API key, which you can get [api.together.xyz](https://api.together.xyz/settings/api-keys). "
    "You can also learn how to build this app step by step by [following streamlit tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
together_api_key = st.text_input("Together API Key", type="password")
if not together_api_key:
    st.info("Please add your Together API key to continue.", icon="🗝️")
else:

    together = Together(api_key=together_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
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
        st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})

