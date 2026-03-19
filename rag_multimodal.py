import os
import chromadb
from groq import Groq
from sentence_transformers import SentenceTransformer
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# Load models
text_model  = SentenceTransformer("all-MiniLM-L6-v2")
image_model = SentenceTransformer("clip-ViT-B-32")

# Load ChromaDB
client    = chromadb.PersistentClient(path="./chroma_db_multimodal")
text_col  = client.get_or_create_collection("text_collection")
image_col = client.get_or_create_collection("image_collection")

# Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_text(query: str):
    # Embed query with text model for text search
    text_embedding = text_model.encode(query).tolist()

    # Embed query with CLIP for image search
    clip_embedding = image_model.encode(query).tolist()

    # Retrieve top 5 text chunks
    results = text_col.query(
        query_embeddings=[text_embedding],
        n_results=5
    )

    # Build context
    context = ""
    sources = []
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        context += f"\n---\n{doc}\n"
        sources.append({
            "text": doc,
            "source": meta.get("source", "unknown"),
            "type": meta.get("type", "text")
        })

    # Search images using CLIP embedding
    image_results = image_col.query(
        query_embeddings=[clip_embedding],
        n_results=3
    )
    matched_images = []
    for i, doc in enumerate(image_results["documents"][0]):
        meta = image_results["metadatas"][0][i]
        matched_images.append({
            "filename": meta.get("filename", ""),
            "path": meta.get("path", ""),
            "ocr_text": meta.get("ocr_text", "")
        })

    # Send to Groq
    prompt = f"""You are a Tamil Nadu driving license and traffic rules assistant.
Based ONLY on the information provided below, answer the user's question
clearly and precisely.
Use numbered steps for procedures.
Include official links if available.
Mention fines and fees clearly if asked.
If the information is not available say so honestly.

INFORMATION:
{context}

USER QUESTION: {query}

Give a clear structured answer with links and fines where relevant."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content, sources, matched_images


def ask_image(image_path: str, query: str = "What is this traffic sign?"):
    # Embed uploaded image using CLIP
    img = Image.open(image_path).convert("RGB")
    image_embedding = image_model.encode(img).tolist()

    # Search image collection using CLIP (512 dim)
    image_results = image_col.query(
        query_embeddings=[image_embedding],
        n_results=3
    )

    matched_images = []
    image_context = ""
    for i, doc in enumerate(image_results["documents"][0]):
        meta = image_results["metadatas"][0][i]
        matched_images.append({
            "filename": meta.get("filename", ""),
            "path": meta.get("path", ""),
            "ocr_text": meta.get("ocr_text", "")
        })
        image_context += f"\nMatched Sign: {meta.get('filename', '').replace('_', ' ').replace('.jpg', '')} | OCR Text: {meta.get('ocr_text', '')}\n"

    # Search text collection using TEXT model (384 dim)
    # Convert image filename to text query for text search
    sign_name = matched_images[0]["filename"].replace("_", " ").replace(".jpg", "") if matched_images else "traffic sign"
    text_query = f"what is {sign_name} meaning rules fine"
    text_embedding = text_model.encode(text_query).tolist()

    text_results = text_col.query(
        query_embeddings=[text_embedding],
        n_results=3
    )
    text_context = ""
    for doc in text_results["documents"][0]:
        text_context += f"\n---\n{doc}\n"

    # Send to Groq
    prompt = f"""You are a Tamil Nadu traffic signs expert.
The user has uploaded a traffic sign image.
Based on the matched sign information below, explain:
1. What this sign means
2. What drivers must do when they see this sign
3. Fine for violating this sign if applicable

MATCHED SIGN INFO:
{image_context}

RELATED RULES:
{text_context}

Give a clear and helpful explanation."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content, matched_images