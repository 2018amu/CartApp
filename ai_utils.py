import os
import faiss
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# -----------------------------
# Embedding model
# -----------------------------
embed_model = SentenceTransformer('all-MiniLM-L6-v2')  # fast small model

# -----------------------------
# FAISS index (in-memory)
# -----------------------------
faiss_index = None
corpus_texts = []   # List of strings
corpus_ids = []     # List of identifiers

# -----------------------------
# Build FAISS index with QA context
# -----------------------------
def build_faiss_index_with_qa(services_docs):
    """
    Build FAISS index using:
      - service names
      - subservice names
      - questions + answers
    """
    global faiss_index, corpus_texts, corpus_ids
    corpus_texts = []
    corpus_ids = []

    for service in services_docs:
        service_id = service.get("id")
        service_name = service.get("name", {}).get("en", "")
        # Add service itself
        if service_name:
            corpus_texts.append(service_name)
            corpus_ids.append(f"{service_id}-service")
        # Add subservices
        for sub in service.get("subservices", []):
            sub_id = sub.get("id", "sub")
            sub_name = sub.get("name", {}).get("en", "")
            if sub_name:
                corpus_texts.append(sub_name)
                corpus_ids.append(f"{service_id}-{sub_id}-subservice")
            # Add questions + answers
            for q in sub.get("questions", []):
                q_id = q.get("id", "q")
                question_text = q.get("q", {}).get("en", "")
                answer_text = q.get("answer", {}).get("en", "")
                if question_text:
                    corpus_texts.append(question_text)
                    corpus_ids.append(f"{service_id}-{sub_id}-{q_id}-q")
                if answer_text:
                    corpus_texts.append(answer_text)
                    corpus_ids.append(f"{service_id}-{sub_id}-{q_id}-a")

    # Encode embeddings
    embeddings = embed_model.encode(corpus_texts, convert_to_numpy=True)
    dim = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dim)
    faiss_index.add(embeddings)

# -----------------------------
# Query FAISS index
# -----------------------------
def query_faiss(query_text, k=3):
    if faiss_index is None or len(corpus_texts) == 0:
        return []
    query_vec = embed_model.encode([query_text], convert_to_numpy=True)
    D, I = faiss_index.search(query_vec, k)
    results = []
    for idx in I[0]:
        if idx < len(corpus_texts):
            results.append({
                "id": corpus_ids[idx],
                "text": corpus_texts[idx]
            })
    return results

# -----------------------------
# LLM completion with context
# -----------------------------
def llm_answer(query_text, context_docs):
    """
    Generate concise answer using LLM with context
    """
    context_str = "\n\n".join([f"[{d['id']}] {d['text']}" for d in context_docs])
    prompt = (
        f"Answer the question concisely using the context below. "
        f"Cite the sources using [id].\n\nContext:\n{context_str}\n\n"
        f"Question: {query_text}\nAnswer:"
    )

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    answer_text = resp.choices[0].message.content.strip()

    # Log audit
    with open("ai_audit_log.jsonl", "a", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.utcnow().isoformat(),
            "query": query_text,
            "context_ids": [d["id"] for d in context_docs],
            "answer": answer_text
        }, f)
        f.write("\n")

    return answer_text
