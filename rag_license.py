import os
import chromadb
from groq import Groq
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_db_license")
collection = client.get_or_create_collection("tn_license")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_license(query: str):

    # Handle greetings separately
    greetings = ["hello", "hi", "hey", "good morning", "good evening", "vanakkam"]
    if query.lower().strip() in greetings:
        return "Welcome to Tamil Nadu Driving License Assistant! 🚗\n\nI can help you with:\n- How to apply for Learner's License\n- How to apply for Permanent License\n- License Renewal procedure\n- Required documents and fees\n- RTO related queries\n\nWhat would you like to know?", []

    # Step 1 — Embed query
    query_embedding = model.encode(query).tolist()

    # Step 2 — Retrieve top 5 chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    # Step 3 — Build context
    context = ""
    sources = []
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        context += f"\n---\n{doc}\n"
        sources.append({
            "text": doc,
            "source": meta.get("source", "TN License Guide"),
            "page": meta.get("page", "-")
        })

    # Step 4 — Precise prompt
    prompt = f"""You are a precise Tamil Nadu driving license assistant.
Your job is to give short, accurate, step by step answers.

STRICT RULES:
- Answer ONLY from the information provided below
- Always include official links from the information if available
- Use numbered steps for procedures
- Keep answers concise and to the point
- If fee is mentioned, always state it clearly
- If a form is needed, mention the form number
- End every answer with the most relevant official link
- Do NOT return Python objects, lists or tuples
- Return only clean plain text answer

INFORMATION:
{context}

USER QUESTION: {query}

Give a precise, short, structured answer with relevant links."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content
    return answer, sources