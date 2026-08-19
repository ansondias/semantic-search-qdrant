"""
Core library for the Qdrant semantic-search application.

Wraps the two moving parts of the workflow:
    1. an embedding model  (Sentence Transformers -> all-MiniLM-L6-v2, 384 dims)
    2. a Qdrant collection  (cosine distance)

Steps implemented here:
    Step 1  - embedding technique (Sentence Transformers)
    Step 4  - connect to a locally running Qdrant instance
    Step 5  - create a collection with the right vector dimension
    Step 6  - store vectors + text/metadata (payload)
    Step 8  - embed a query with the SAME model
    Step 9  - cosine similarity search
    Step 10 - return Top-K with scores
    Step 12 - optional metadata filtering
"""

from __future__ import annotations

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue, Range,
)

MODEL_NAME = "all-MiniLM-L6-v2"   # 384-dim, tuned for semantic similarity
DISTANCE = Distance.COSINE        # cosine similarity (Step 9)


class SemanticSearch:
    def __init__(self, collection: str, url: str = "http://localhost:6333"):
        self.collection = collection
        # Step 1: load the embedding model
        self.model = SentenceTransformer(MODEL_NAME)
        self.dim = self.model.get_sentence_embedding_dimension()
        # Step 4: connect to the local Qdrant instance
        self.client = QdrantClient(url=url)

    # ---- Step 3 / 8: text -> vector -------------------------------------
    def embed(self, texts: list[str]):
        # normalize_embeddings=True pairs cleanly with cosine distance
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    # ---- Step 5: create the collection ----------------------------------
    def create_collection(self, recreate: bool = True):
        if recreate and self.client.collection_exists(self.collection):
            self.client.delete_collection(self.collection)
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=self.dim, distance=DISTANCE),
            )
        return self.client.get_collection(self.collection)

    # ---- Step 6: store vectors + payload --------------------------------
    def index(self, documents: list[dict]):
        vectors = self.embed([d["text"] for d in documents])
        points = [
            PointStruct(id=i, vector=vec, payload=doc)
            for i, (vec, doc) in enumerate(zip(vectors, documents))
        ]
        self.client.upsert(collection_name=self.collection, points=points)
        return len(points)

    # ---- Steps 8-10: query -> embedding -> similarity -> Top-K ----------
    def search(self, query: str, top_k: int = 3, query_filter: Filter | None = None):
        qvec = self.embed([query])[0]
        hits = self.client.query_points(
            collection_name=self.collection,
            query=qvec,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        ).points
        return hits

    # ---- Step 12: convenience builder for a category filter -------------
    @staticmethod
    def category_filter(category: str) -> Filter:
        return Filter(must=[FieldCondition(key="category",
                                           match=MatchValue(value=category))])

    @staticmethod
    def year_gte_filter(year: int) -> Filter:
        return Filter(must=[FieldCondition(key="year", range=Range(gte=year))])


def print_hits(query: str, hits, note: str = ""):
    """Pretty-print Top-K results for the console / report."""
    header = f'Query: "{query}"'
    if note:
        header += f"   [{note}]"
    print("\n" + header)
    print("-" * len(header))
    if not hits:
        print("  (no results)")
        return
    for rank, h in enumerate(hits, 1):
        p = h.payload
        print(f"  {rank}. score={h.score:.4f}  "
              f"[{p.get('category','?'):<10}] {p['text'][:80]}...")
