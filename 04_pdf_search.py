"""
Step 13: Document-based semantic search (PDF input).

Pipeline:
    PDF -> extract text (pypdf) -> split into chunks -> embed each chunk
        -> store in a dedicated Qdrant collection -> semantic search over it.

This makes a real document searchable by meaning: you ask a question in plain
English and get back the passage that answers it, with a similarity score.

Run:  python 04_pdf_search.py
(If data/sample.pdf is missing, a sample PDF is generated first.)
"""
import os
import re
from pypdf import PdfReader

from qsearch import SemanticSearch, print_hits
from qdrant_client.models import PointStruct

COLLECTION = "pdf_semantic_search"
PDF_PATH = "data/sample.pdf"


SAMPLE_PARAGRAPHS = [
    ("Introduction to Vector Databases",
     "A vector database is a system designed to store and query high-dimensional "
     "vectors, which are numerical representations of data such as text, images, or "
     "audio. Unlike traditional databases that match exact values, a vector database "
     "finds items by similarity of meaning."),
    ("Embeddings",
     "An embedding is a dense list of numbers that captures the semantic content of a "
     "piece of text. Sentences with similar meaning are mapped to nearby points in the "
     "vector space, even if they share no words in common. Models such as Sentence "
     "Transformers produce these embeddings."),
    ("Similarity Search",
     "To answer a query, the query itself is embedded and compared against stored "
     "vectors using a distance metric such as cosine similarity. The database returns "
     "the nearest vectors, which correspond to the most semantically relevant documents."),
    ("Approximate Nearest Neighbor",
     "Searching millions of vectors exhaustively is slow, so vector databases use "
     "approximate nearest neighbor algorithms like HNSW. These build a graph index that "
     "trades a tiny amount of accuracy for a very large gain in query speed."),
    ("Use Cases",
     "Semantic search powers many applications: retrieval-augmented generation for "
     "chatbots, recommendation systems, image search, deduplication, and anomaly "
     "detection. Qdrant is an open-source vector database built for these workloads."),
]


def generate_sample_pdf(path: str):
    """Create a small multi-paragraph PDF so the demo is self-contained."""
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

    os.makedirs(os.path.dirname(path), exist_ok=True)
    styles = getSampleStyleSheet()
    story = [Paragraph("A Short Guide to Semantic Search", styles["Title"]),
             Spacer(1, 12)]
    for title, body in SAMPLE_PARAGRAPHS:
        story.append(Paragraph(title, styles["Heading2"]))
        story.append(Paragraph(body, styles["BodyText"]))
        story.append(Spacer(1, 10))
    SimpleDocTemplate(path, pagesize=LETTER).build(story)


def extract_chunks(path: str, sentences_per_chunk: int = 2) -> list[str]:
    """Extract text from the PDF and split it into overlapping sentence chunks.

    PDF text extraction rarely preserves paragraph breaks, so we normalise the
    text and chunk it by sentences (a robust, standard RAG approach) rather than
    relying on blank lines.
    """
    reader = PdfReader(path)
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    text = re.sub(r"\s+", " ", text).strip()          # collapse newlines/spaces
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk = " ".join(sentences[i:i + sentences_per_chunk])
        if len(chunk) > 40:
            chunks.append(chunk)
    return chunks


def main():
    if not os.path.exists(PDF_PATH):
        print(f"Generating sample PDF at {PDF_PATH} ...")
        generate_sample_pdf(PDF_PATH)

    ss = SemanticSearch(COLLECTION)
    ss.create_collection(recreate=True)

    chunks = extract_chunks(PDF_PATH)
    print(f"Extracted {len(chunks)} text chunks from {PDF_PATH}")

    vectors = ss.embed(chunks)
    points = [
        PointStruct(id=i, vector=v,
                    payload={"text": c, "source": os.path.basename(PDF_PATH), "chunk": i})
        for i, (v, c) in enumerate(zip(vectors, chunks))
    ]
    ss.client.upsert(COLLECTION, points=points)
    print(f"Indexed {len(points)} chunks into '{COLLECTION}'.\n")

    for q in ["How does the database make search fast?",
              "What is an embedding?",
              "Where is semantic search used in practice?"]:
        print_hits(q, ss.search(q, top_k=2))


if __name__ == "__main__":
    main()
