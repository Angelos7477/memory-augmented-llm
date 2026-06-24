import streamlit as st

from core.llm_client import generate_response
from core.memory_manager import (retrieve_context, store_chat_summary, restore_memory, mark_memory_obsolete,
                                 store_user_memory, store_user_preference, should_store_memory, get_user_memories)
from core.prompt_builder import build_messages
from core.logger import log_prompt
from core.summarizer import update_session_summary
from core.memory_classifier import classify_memory
import uuid
import time

def render_memory_sidebar(user_id: str) -> None:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Long-Term Memory")

    memory_status = st.sidebar.radio(
        "Status",
        ["active", "obsolete"],
        horizontal=True
    )

    user_memories = get_user_memories(
        user_id=user_id,
        status=memory_status
    )

    preferences = [
        memory for memory in user_memories
        if memory["metadata"].get("memory_type") == "preference"
    ]

    facts = [
        memory for memory in user_memories
        if memory["metadata"].get("memory_type") == "user_memory"
    ]

    chat_summaries = [
        memory for memory in user_memories
        if memory["metadata"].get("memory_type") == "chat_summary"
    ]

    action_label = (
        "Mark Obsolete"
        if memory_status == "active"
        else "Restore"
    )

    action_type = (
        "obsolete"
        if memory_status == "active"
        else "restore"
    )

    def render_memory_item(memory: dict) -> None:
        st.write("•", memory["text"])

        if st.button(
            action_label,
            key=f"{action_type}_{memory['id']}"
        ):
            if action_type == "obsolete":
                mark_memory_obsolete(
                    memory_id=memory["id"],
                    reason="manual_sidebar_action"
                )
            else:
                restore_memory(
                    memory_id=memory["id"],
                    reason="manual_sidebar_action"
                )

            st.rerun()

    def render_memory_group(title: str, memories: list[dict]) -> None:
        with st.sidebar.expander(f"{title} ({len(memories)})"):
            if memories:
                for memory in memories:
                    render_memory_item(memory)
                    st.markdown("---")
            else:
                st.caption("No memories stored.")

    render_memory_group("Preferences", preferences)
    render_memory_group("User Memories", facts)
    render_memory_group("Chat Summaries", chat_summaries)

st.set_page_config(
    page_title="Memory-Augmented LLM Chatbot",
    page_icon="🧠"
)

st.title("🧠 Memory-Augmented LLM Chatbot")
st.caption("Memory-Augmented Chatbot with OpenAI, Embeddings and ChromaDB")


user_id = st.sidebar.text_input("User ID", value="default_user")

new_chat_clicked = st.sidebar.button("New Chat")

save_clicked = st.sidebar.button("Save Chat Summary In Long-Term Memory")

st.sidebar.markdown("---")
st.sidebar.subheader("Evaluation Controls")
if "memory_enabled" not in st.session_state:
    st.session_state.memory_enabled = True

button_label = (
    "🟢 Memory ON"
    if st.session_state.memory_enabled
    else "🔴 Memory OFF"
)
if st.sidebar.button(button_label):
    st.session_state.memory_enabled = (
        not st.session_state.memory_enabled
    )
    st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_summary" not in st.session_state:
    st.session_state.session_summary = ""

if "exchanges_since_summary" not in st.session_state:
    st.session_state.exchanges_since_summary = 0

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

#Show seassion id for testing purposes
st.sidebar.caption("Current Session ID")
st.sidebar.code(st.session_state.session_id)    

if "saved_chat_summary_id" not in st.session_state:
    st.session_state.saved_chat_summary_id = None

if "last_context" not in st.session_state:
    st.session_state.last_context = None

if "last_classification" not in st.session_state:
    st.session_state.last_classification = None

if "last_storage_log" not in st.session_state:
    st.session_state.last_storage_log = None


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
    st.session_state.last_context = None
    st.session_state.last_classification = None
    st.session_state.last_storage_log = None

    st.success("New chat started.")
    st.rerun()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Write your message...")

if not user_input:
    render_memory_sidebar(user_id)

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    
    if st.session_state.memory_enabled:
        retrieval_start = time.perf_counter()
        context = retrieve_context(user_input, user_id=user_id)
        retrieval_latency_ms = round((time.perf_counter() - retrieval_start) * 1000, 2)
    else: 
        context= {"preferences": [],"user_memories": [],"chat_summaries": []}
        retrieval_latency_ms = 0
    messages_for_llm = build_messages(
        user_input=user_input,
        context=context,
        session_summary=st.session_state.session_summary,
        conversation_messages=st.session_state.messages
    )

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            llm_start = time.perf_counter()
            assistant_response = generate_response(messages_for_llm)
            llm_latency_ms = round(
                (time.perf_counter() - llm_start) * 1000,
                2
            )
            total_latency_ms = round(
                retrieval_latency_ms + llm_latency_ms,
                2
            )
            st.write(assistant_response)
            st.caption(
                f"Total Latency: {total_latency_ms} ms "
                f"(retrieval Latency: {retrieval_latency_ms} ms, "
                f"LLM Latency: {llm_latency_ms} ms)"
            )

    classification = classify_memory(user_input)

    memory_storage_log = []
    if st.session_state.memory_enabled:
        for memory in classification.get("memories", []):
            memory_type = memory.get("memory_type")
            memory_text = memory.get("memory_text")
            confidence = memory.get("confidence", 0)

            if confidence < 0.7:
                memory_storage_log.append({
                    "memory_type": memory_type,
                    "memory_text": memory_text,
                    "confidence": confidence,
                    "stored": False,
                    "reason": "low_confidence",
                    "closest_memory": None,
                    "distance": None,
                    "threshold": None
                })
                continue

            if memory_type == "ignore":
                memory_storage_log.append({
                    "memory_type": memory_type,
                    "memory_text": memory_text,
                    "confidence": confidence,
                    "stored": False,
                    "reason": "ignored_by_classifier",
                    "closest_memory": None,
                    "distance": None,
                    "threshold": None
                })
                continue

            storage_decision = should_store_memory(
                text=memory_text,
                user_id=user_id,
                memory_type=memory_type
            )

            stored = False

            if storage_decision["store"]:
                if memory_type == "preference":
                    store_user_preference(
                        memory_text,
                        user_id=user_id
                    )
                    stored = True

                elif memory_type == "user_memory":
                    store_user_memory(
                        memory_text,
                        user_id=user_id
                    )
                    stored = True

            memory_storage_log.append({
                "memory_type": memory_type,
                "memory_text": memory_text,
                "confidence": confidence,
                "stored": stored,
                "reason": storage_decision["reason"],
                "closest_memory": storage_decision["closest_memory"],
                "distance": storage_decision["distance"],
                "threshold": storage_decision["threshold"]
            })
    else: 
        classification = {"memories": []}
    #Keep session states
    st.session_state.last_context = context
    st.session_state.last_classification = classification
    st.session_state.last_storage_log = memory_storage_log
    #Update of memories on the sidebar
    render_memory_sidebar(user_id)

    
    log_prompt(
        user_input=user_input,
        context=context,
        session_summary=st.session_state.session_summary,
        messages_for_llm=messages_for_llm,
        assistant_response=assistant_response,
        user_id=user_id,
        session_id=st.session_state.session_id,
        memory_enabled=st.session_state.memory_enabled,
        retrieval_latency_ms=retrieval_latency_ms,
        llm_latency_ms=llm_latency_ms,
        total_latency_ms=total_latency_ms,
        classification=classification,
        memory_storage=memory_storage_log
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

#with st.expander("📝 Current Session Summary", expanded=True):
#    if st.session_state.session_summary:
#        st.write(st.session_state.session_summary)
#    else:
#        st.info("No session summary yet.")

if st.session_state.session_summary:
    with st.expander(
        "📝 Current Session Summary",
        expanded=False
    ):
        st.write(
            st.session_state.session_summary
        )

if st.session_state.last_context is not None:
    with st.expander("🔎 Retrieved Context"):
        st.write("### Preferences")
        st.json(st.session_state.last_context.get("preferences", []))

        st.write("### User Memories")
        st.json(st.session_state.last_context.get("user_memories", []))

        st.write("### Chat Summaries")
        st.json(st.session_state.last_context.get("chat_summaries", []))

if st.session_state.last_classification is not None:
    with st.expander("🏷️ Memory Classification"):
        st.json(st.session_state.last_classification)

if st.session_state.last_storage_log is not None:
    with st.expander("🧠 Memory Storage Decision"):
        st.json(st.session_state.last_storage_log)