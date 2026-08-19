"""
Steps 3-6: generate embeddings for the corpus and store them in Qdrant.

Run:  python 01_ingest.py
"""
from qsearch import SemanticSearch
from documents import DOCUMENTS

COLLECTION = "semantic_search_docs"


def main():
    ss = SemanticSearch(COLLECTION)
    print(f"Embedding model : {ss.model.__class__.__name__} / all-MiniLM-L6-v2")
    print(f"Vector dimension: {ss.dim}")
    print(f"Distance metric : cosine")

    info = ss.create_collection(recreate=True)
    print(f"\nCreated collection '{COLLECTION}'.")

    n = ss.index(DOCUMENTS)
    print(f"Indexed {n} documents (vectors + metadata payload).")

    count = ss.client.count(COLLECTION).count
    print(f"Points now in collection: {count}")


if __name__ == "__main__":
    main()
