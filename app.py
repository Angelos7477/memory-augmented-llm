import streamlit as st

from core.llm_client import generate_response
from core.memory_manager import retrieve_context, store_chat_summary, retrieve_context, store_chat_summary, store_user_memory, store_user_preference
from core.prompt_builder import build_messages
from core.logger import log_prompt
from core.summarizer import update_session_summary
from core.memory_classifier import classify_memory
import uuid


st.set_page_config(
    page_title="Memory-Augmented LLM Chatbot",
    page_icon="🧠"
)

st.title("🧠 Memory-Augmented LLM Chatbot")
st.caption("Memory-Augmented Chatbot with OpenAI, Embeddings and ChromaDB")

col1, col2 = st.columns(2)
with col1:
    new_chat_clicked = st.button("New Chat")
with col2:
    save_clicked = st.button("Save Chat Summary In Long-Term Memory")

user_id = st.sidebar.text_input(
    "User ID",
    value="default_user"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_summary" not in st.session_state:
    st.session_state.session_summary = ""

if "exchanges_since_summary" not in st.session_state:
    st.session_state.exchanges_since_summary = 0

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "saved_chat_summary_id" not in st.session_state:
    st.session_state.saved_chat_summary_id = None

if save_clicked:
    if st.session_state.messages:
        if st.session_state.session_summary == "":
            final_summary = update_session_summary(
                current_summary="",
                messages_to_summarize=st.session_state.messages
            )
        elif st.session_state.exchanges_since_summary > 1:
            final_summary = update_session_summary(
                current_summary=st.session_state.session_summary,
                messages_to_summarize=st.session_state.messages[-6:]
            )
        else:
            final_summary = st.session_state.session_summary

        st.session_state.session_summary = final_summary

        st.session_state.saved_chat_summary_id = store_chat_summary(
            text=final_summary,
            session_id=st.session_state.session_id,
            user_id=user_id,
            existing_id=st.session_state.saved_chat_summary_id
        )

        st.success("Chat summary saved.")
    else:
        st.warning("No messages to summarize.")

if new_chat_clicked:
    st.session_state.messages = []
    st.session_state.session_summary = ""
    st.session_state.exchanges_since_summary = 0
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.saved_chat_summary_id = None

    st.success("New chat started.")
    st.rerun()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Write your message...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    context = retrieve_context(user_input, user_id=user_id)

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
    
    classification = classify_memory(user_input)
    memory_type = classification["memory_type"]
    memory_text = classification["memory_text"]
    if memory_type == "preference":
        store_user_preference(
            text=memory_text,
            user_id=user_id
        )
    elif memory_type == "user_memory":
        store_user_memory(
            text=memory_text,
            user_id=user_id
        )

    log_prompt(
        user_input=user_input,
        context=context,
        session_summary=st.session_state.session_summary,
        messages_for_llm=messages_for_llm,
        assistant_response=assistant_response,
        classification=classification
    )

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_response}
    )
    st.session_state.exchanges_since_summary += 1
    if st.session_state.exchanges_since_summary >= 4:

        if st.session_state.session_summary == "":
            messages_to_summarize = st.session_state.messages[:8]
        else:
            messages_to_summarize = st.session_state.messages[-6:]

        st.session_state.session_summary = (
            update_session_summary(
                current_summary=st.session_state.session_summary,
                messages_to_summarize=messages_to_summarize
            )
        )
        st.session_state.exchanges_since_summary = 1