# Memory-Augmented LLM

A conversational AI assistant that extends the capabilities of Large Language Models (LLMs) with long-term memory using embeddings and vector databases.

This project is developed as part of a thesis on memory mechanisms in LLM-based conversational systems.

---

## Features

### Long-Term Memory

Long-term memories are stored in ChromaDB using vector embeddings.

Supported memory types:

- User Preferences
  - Preferred response style
  - Communication preferences
  - Custom assistant behavior

- User Memories
  - Personal information
  - Interests and goals
  - Persistent user facts

### Short-Term Memory

Short-term memory is maintained during the current conversation session.
Το σύστημα διατηρεί στο prompt τα τρία τελευταία ολοκληρωμένα ζεύγη user-assistant της τρέχουσας συνεδρίας, μαζί με το τρέχον ερώτημα του χρήστη.
Components:

- Session Summary
  - Compact representation of previous conversation context
  - Continuously updated during the session

- Recent Conversation History
  - Last 3 user-assistant exchanges
  - Preserved in their original form

### Memory Retrieval

The system retrieves relevant information using semantic similarity search.

Retrieved context may include:

- Active user preferences
- Relevant user memories
- Current session summary
- Recent conversation history

---

## Memory Management

### Memory States

Each long-term memory can be in one of two states:

- Active
- Obsolete

Only active memories are considered during retrieval.

### Context Compaction

To reduce context window usage:

- Recent messages are preserved
- Older messages are summarized into the session summary
- The summary is continuously updated throughout the conversation

### Session Completion

At the end of a conversation session:

- A final chat summary can be generated
- The summary can be stored as long-term memory
- A new session can then be started

---

## System Architecture

User Input
↓
Embedding Generation
↓
Memory Retrieval
↓
Prompt Construction
↓
LLM Response Generation
↓
Memory Update

---

## Technologies

- Python
- Streamlit
- OpenAI API
- OpenAI Embeddings
- ChromaDB

---

## Project Structure

```text
memory-augmented-llm/
│
├── app.py
│
├── core/
│   ├── llm_client.py
│   ├── embedding_client.py
│   ├── memory_manager.py
│   └── prompt_builder.py
│
├── data/
│   └── chroma_db/
│
├── tests/
│
└── README.md
```

---

## Thesis Goal

The goal of this project is to investigate how vector databases and embeddings can be used to provide long-term memory capabilities to Large Language Models, overcoming the limitations of fixed context windows.

to run 
-- 
streamlit run app.py