Memory-Augmented LLM
====================

A conversational AI assistant that extends the capabilities of Large Language Models (LLMs) with long-term memory using embeddings and vector databases.

This project was developed as part of a Master's thesis on memory mechanisms in LLM-based conversational systems.

* * * * *

Features
--------

### Long-Term Memory

Long-term memories are stored in ChromaDB using vector embeddings and semantic similarity search.

Supported memory types:

-   User Preferences

    -   Preferred response style

    -   Communication preferences

    -   Custom assistant behavior

-   User Memories

    -   Personal information

    -   Interests and goals

    -   Persistent user facts

-   Chat Summaries

    -   Summaries of completed conversation sessions

    -   Stored for future retrieval across sessions

### Short-Term Memory

Short-term memory is maintained during the current conversation session.

The system preserves:

-   The last three user-assistant exchanges

-   The current user message

-   A continuously updated session summary

Components:

-   Session Summary

    -   Compact representation of previous conversation context

    -   Automatically updated during the session

-   Recent Conversation History

    -   Last three user-assistant exchanges

    -   Preserved in their original form

### Memory Retrieval

The system retrieves relevant information using semantic similarity search over stored memories.

Retrieved context may include:

-   Active user preferences

-   Relevant user memories

-   Previous chat summaries

-   Current session summary

-   Recent conversation history

### Memory Evaluation Mode

The application supports enabling or disabling long-term memory during runtime.

Memory ON:

-   Long-term memory retrieval enabled

-   Memory classification enabled

-   Memory storage enabled

Memory OFF:

-   No long-term memory retrieval

-   No long-term memory storage

-   Short-term memory remains available

This feature enables direct comparison between a standard conversational LLM and a memory-augmented LLM.

* * * * *

Memory Management
-----------------

### Memory States

Each long-term memory can be in one of two states:

-   Active

-   Obsolete

Only active memories participate in retrieval.

Obsolete memories remain stored and can be restored later.

### Context Compaction

To reduce context window usage:

-   Recent messages are preserved

-   Older messages are summarized

-   The session summary is continuously updated

### Session Completion

At the end of a conversation:

-   A final chat summary can be generated

-   The summary can be stored as long-term memory

-   A new session can be started using a new Session ID

* * * * *

System Architecture
-------------------

```
User Input
     ↓
Memory Retrieval
     ↓
Prompt Construction
     ↓
LLM Response Generation
     ↓
Memory Classification
     ↓
Memory Storage

```

* * * * *

Evaluation Features
-------------------

The system includes evaluation and debugging tools:

-   Long-Term Memory ON/OFF Toggle

-   Session ID Tracking

-   Retrieved Context Inspection

-   Memory Classification Inspection

-   Memory Storage Decision Inspection

Latency Measurements:

-   Retrieval Latency

-   LLM Generation Latency

-   Total Response Latency

All interactions are logged in JSON format for later analysis.

* * * * *

Technologies
------------

-   Python

-   Streamlit

-   OpenAI API

-   OpenAI Embeddings

-   ChromaDB

* * * * *

Project Structure
-----------------

```
memory-augmented-llm/
│
├── app.py
│
├── core/
│   ├── llm_client.py
│   ├── embedding_client.py
│   ├── memory_manager.py
│   ├── memory_classifier.py
│   ├── prompt_builder.py
│   ├── summarizer.py
│   └── logger.py
│
├── chroma_db/
├── logs/
│
└── README.md

```

* * * * *

Thesis Goal
-----------

The goal of this project is to investigate how embeddings and vector databases can be used to provide long-term memory capabilities to Large Language Models, helping overcome the limitations imposed by fixed context windows.

The project evaluates the impact of memory mechanisms on information recall, conversational consistency, and response latency.

* * * * *

Running the Application
-----------------------

Install dependencies:

```
pip install -r requirements.txt

```

Run the application:

```
streamlit run app.py

```