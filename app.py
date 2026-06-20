import streamlit as st
from core.llm_client import generate_response

st.set_page_config(
    page_title="Memory-Augmented LLM Chatbot",
    page_icon="🧠"
)

st.title("🧠 Memory-Augmented LLM Chatbot")
st.caption("Version 0: Basic chatbot without long-term memory")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        }
    ]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

user_input = st.chat_input("Write your message...")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            assistant_response = generate_response(st.session_state.messages)
            st.write(assistant_response)

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_response}
    )