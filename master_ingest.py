import os
import chromadb
import pdfplumber
import requests
import pandas as pd
from bs4 import BeautifulSoup
from PIL import Image
from sentence_transformers import SentenceTransformer
import easyocr
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────
PDF_FOLDER      = "tn_license/pdf"
IMAGE_FOLDER    = "tn_license/images"
CSV_FOLDER      = "tn_license/csv"
WEB_FILE        = "tn_license/web/urls.txt"
TEXT_FILE       = "tn_license/license_data.txt"
CHROMA_PATH     = "./chroma_db_multimodal"

# ── Models ─────────────────────────────────────────────────
print("🔄 Loading models...")
text_model  = SentenceTransformer("all-MiniLM-L6-v2")
image_model = SentenceTransformer("clip-ViT-B-32")
ocr_reader  = easyocr.Reader(["en"], gpu=False)
print("✅ Models loaded!")

# ── ChromaDB ───────────────────────────────────────────────
client = chromadb.PersistentClient(path=CHROMA_PATH)

try:
    client.delete_collection("text_collection")
    client.delete_collection("image_collection")
except:
    pass

text_col  = client.get_or_create_collection("text_collection")
image_col = client.get_or_create_collection("image_collection")

text_chunks = []

# ── 1. Load license_data.txt ───────────────────────────────
print("\n📄 Reading license_data.txt...")
if os.path.exists(TEXT_FILE):
    with open(TEXT_FILE, "r", encoding="utf-8") as f:
        raw = f.read().replace("\r\n", "\n")
    chunks = [c.strip() for c in raw.split("\n\n") if len(c.strip()) > 50]
    for chunk in chunks:
        text_chunks.append({
            "text": chunk,
            "source": "license_data.txt",
            "type": "text"
        })
    print(f"✅ {len(chunks)} chunks from license_data.txt")

# ── 2. Load PDFs ───────────────────────────────────────────
print("\n📚 Reading PDFs...")
for pdf_file in os.listdir(PDF_FOLDER):
    if not pdf_file.endswith(".pdf"):
        continue
    path = os.path.join(PDF_FOLDER, pdf_file)
    print(f"  📄 Processing: {pdf_file}")
    try:
        with pdfplumber.open(path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extract normal text
                text = page.extract_text()
                if text and len(text.strip()) > 50:
                    text_chunks.append({
                        "text": text.strip(),
                        "source": pdf_file,
                        "type": "pdf_text",
                        "page": page_num + 1
                    })

                # Extract tables
                # Extract tables
                tables = page.extract_tables()
                for table in tables:
                    if not table:
                        continue
                    headers = table[0]
                    
                    # Find Marathi column index to skip
                    skip_indices = []
                    if headers:
                        for idx, h in enumerate(headers):
                            if h and ("marathi" in str(h).lower() or 
                                    "Marathi" in str(h)):
                                skip_indices.append(idx)

                    for row in table[1:]:
                        if not row:
                            continue
                        row_text = " | ".join([
                            f"{str(headers[i]).strip()}: {str(cell).strip()}"
                            for i, cell in enumerate(row)
                            if i not in skip_indices
                            and cell
                            and headers
                            and i < len(headers)
                            and str(cell).strip() != "nan"
                            and str(cell).strip() != "None"
                        ])
                        if len(row_text) > 30:
                            text_chunks.append({
                                "text": row_text,
                                "source": pdf_file,
                                "type": "pdf_table",
                                "page": page_num + 1
                            })
        print(f"  ✅ Done: {pdf_file}")
    except Exception as e:
        print(f"  ❌ Error reading {pdf_file}: {e}")

# ── 3. Load CSV ────────────────────────────────────────────
print("\n📊 Reading CSV files...")
for csv_file in os.listdir(CSV_FOLDER):
    if not csv_file.endswith(".csv"):
        continue
    path = os.path.join(CSV_FOLDER, csv_file)
    print(f"  📊 Processing: {csv_file}")
    try:
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            row_text = " | ".join([
                f"{col}: {str(val).strip()}"
                for col, val in row.items()
                if str(val).strip() != "nan"
            ])
            if len(row_text) > 20:
                text_chunks.append({
                    "text": row_text,
                    "source": csv_file,
                    "type": "csv"
                })
        print(f"  ✅ Done: {csv_file} — {len(df)} rows")
    except Exception as e:
        print(f"  ❌ Error reading {csv_file}: {e}")

# ── 4. Scrape Websites ─────────────────────────────────────
print("\n🌐 Scraping websites...")
if os.path.exists(WEB_FILE):
    with open(WEB_FILE, "r") as f:
        urls = [u.strip() for u in f.readlines() if u.strip()]

    for url in urls:
        print(f"  🌐 Scraping: {url}")
        try:
            res = requests.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0"
            })
            soup = BeautifulSoup(res.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n")
            lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 50]
            chunks = []
            current = ""
            for line in lines:
                current += " " + line
                if len(current) > 500:
                    chunks.append(current.strip())
                    current = ""
            if current.strip():
                chunks.append(current.strip())
            for chunk in chunks:
                text_chunks.append({
                    "text": chunk,
                    "source": url,
                    "type": "web"
                })
            print(f"  ✅ Done: {len(chunks)} chunks from {url}")
        except Exception as e:
            print(f"  ❌ Error scraping {url}: {e}")

# ── 5. Embed and Store Text ────────────────────────────────
print(f"\n🔄 Embedding {len(text_chunks)} text chunks...")
batch_size = 50
for i in range(0, len(text_chunks), batch_size):
    batch = text_chunks[i:i+batch_size]
    texts = [c["text"] for c in batch]
    embeddings = text_model.encode(texts).tolist()
    text_col.add(
        ids=[f"text_{i+j}" for j in range(len(batch))],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{
            "source": c.get("source", "unknown"),
            "type": c.get("type", "text"),
            "page": str(c.get("page", "-"))
        } for c in batch]
    )
    print(f"  ✅ Embedded batch {i//batch_size + 1}")

print(f"✅ {len(text_chunks)} text chunks stored!")

# ── 6. Embed and Store Images ──────────────────────────────
print("\n🖼️ Embedding images...")
image_count = 0
for img_file in os.listdir(IMAGE_FOLDER):
    if not img_file.lower().endswith((".jpg", ".jpeg", ".png")):
        continue
    path = os.path.join(IMAGE_FOLDER, img_file)
    try:
        img = Image.open(path).convert("RGB")
        embedding = image_model.encode(img).tolist()

        # OCR to get text from image
        ocr_result = ocr_reader.readtext(path, detail=0)
        ocr_text = " ".join(ocr_result) if ocr_result else img_file

        image_col.add(
            ids=[f"img_{image_count}"],
            embeddings=[embedding],
            documents=[ocr_text if ocr_text else img_file],
            metadatas=[{
                "filename": img_file,
                "path": path,
                "type": "image",
                "ocr_text": ocr_text
            }]
        )
        image_count += 1
        print(f"  ✅ Embedded: {img_file} | OCR: {ocr_text[:50]}")
    except Exception as e:
        print(f"  ❌ Error: {img_file}: {e}")

print(f"✅ {image_count} images stored!")
print("\n🎉 Master ingestion complete!")
print(f"   📝 Text chunks: {len(text_chunks)}")
print(f"   🖼️  Images: {image_count}")