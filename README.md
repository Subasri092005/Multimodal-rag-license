#  TN License & Traffic Assistant

AI-powered RAG application for Tamil Nadu driving license and traffic rules.

## Features
- 💬 License & Traffic Q&A
- 🚦 Traffic Sign Identifier
- 🏛️ RTO Office Finder

## Tech Stack
- Python
- Streamlit
- ChromaDB
- Sentence Transformers (CLIP + MiniLM)
- Groq LLaMA 3.3 70B

## Setup

### 1. Clone the repo
git clone https://github.com/Subasri092005/Multimodal-rag-license

### 2. Install dependencies
pip install -r requirements.txt

### 3. Add API keys
Create a .env file:
GROQ_API_KEY=your_groq_key_here

### 4. Run ingestion
python master_ingest.py

### 5. Run the app
streamlit run app_multimodal.py