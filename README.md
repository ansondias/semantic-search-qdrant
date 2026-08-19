# Semantic Search with Qdrant

A Python semantic-search app: text → **Sentence-Transformer embeddings** (all-MiniLM-L6-v2,
384-dim) → stored in **Qdrant** with metadata → **cosine similarity** search returning Top-K
results. Includes metadata filtering and PDF document search.

## 1. Run Qdrant (Docker)

```bash
docker pull qdrant/qdrant
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant
# Dashboard: http://localhost:6333/dashboard
```

## 2. Install

```bash
python3 -m venv venv && source venv/bin/activate
pip install qdrant-client sentence-transformers pypdf reportlab
```

## 3. Run the workflow

```bash
python 01_ingest.py            # embed 14 docs + store in Qdrant
python 02_search.py            # run demo queries (Top-3 + scores)
python 02_search.py "your natural language query"
python 02_search.py -i         # interactive prompt
python 03_metadata_filter.py   # similarity search + payload filters
python 04_pdf_search.py        # PDF -> chunks -> embed -> search
```

## Files

| File | Purpose |
|------|---------|
| `qsearch.py` | Core library — embedding model + Qdrant collection (steps 1, 4–10, 12) |
| `documents.py` | The 14-document corpus with metadata |
| `01_ingest.py` | Create collection, embed, store vectors + payload |
| `02_search.py` | Query → embed → cosine similarity → Top-K |
| `03_metadata_filter.py` | Vector search combined with payload filters |
| `04_pdf_search.py` | Document-based semantic search over a PDF |
| `build_report.py` | Regenerates `report.html` (live output + screenshots) |
| `report.pdf` / `report.html` | The full report |
| `screenshots/` | Dashboard screenshots + embedding-space plot |

## Model / distance

- **Embedding:** `sentence-transformers/all-MiniLM-L6-v2` — 384 dimensions
- **Distance:** cosine similarity (embeddings L2-normalized)
