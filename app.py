import streamlit as st

from core.llm_client import generate_response
from core.memory_manager import retrieve_context
from core.prompt_builder import build_messages
from core.logger import log_prompt

st.set_page_config(
    page_title="Memory-Augmented LLM Chatbot",
    page_icon="🧠"
)

st.title("🧠 Memory-Augmented LLM Chatbot")
st.caption("Memory-Augmented Chatbot with OpenAI, Embeddings and ChromaDB")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_summary" not in st.session_state:
    st.session_state.session_summary = ""

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Write your message...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    context = retrieve_context(user_input)

    messages_for_llm = build_messages(
        user_input=user_input,
        context=context,
        session_summary=st.session_state.session_summary,
        conversation_messages=st.session_state.messages
    )

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            assistant_response = generate_response(messages_for_llm)
            st.write(assistant_response)

    log_prompt(
        user_input=user_input,
        context=context,
        session_summary=st.session_state.session_summary,
        messages_for_llm=messages_for_llm,
        assistant_response=assistant_response
    )

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_response}
    )