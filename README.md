# memory-augmented-llm
Memory-Augmented LLM Chatbot using Embeddings and Vector Databases


1. session_memory
   Βραχυπρόθεσμη μνήμη της τρέχουσας συνομιλίας.
   Δεν χρειάζεται απαραίτητα ChromaDB.
   Ζει στο st.session_state με session_id.

2. preference_memory
   Σταθερές οδηγίες για το πώς θέλει ο χρήστης να απαντάει το AI.
   Π.χ. "θέλω σύντομες απαντήσεις", "θέλω αναλυτική εξήγηση".

3. user_memory
   Πληροφορίες για τον χρήστη ή τα ενδιαφέροντά του.
   Π.χ. "με λένε Άγγελο", "μου αρέσουν sci-fi ταινίες", "γράφω διπλωματική".


1. Short-term memory:
   Τα τελευταία μηνύματα στο st.session_state.

2. Long-term user memory:
   Προτιμήσεις και πληροφορίες χρήστη στη ChromaDB.

3. Session summaries:
   Περίληψη συνομιλίας κάθε 10 prompts στη ChromaDB.

4. Forgetting:
   active / obsolete status.

to run 
-- 
streamlit run app.py