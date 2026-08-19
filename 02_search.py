"""
Steps 7-11: accept a natural-language query, embed it, run cosine similarity
search in Qdrant, and display the Top-K most similar documents with scores.

Usage:
    python 02_search.py                 # runs a set of demo queries (Step 11)
    python 02_search.py "your query"    # search a single custom query
    python 02_search.py -i              # interactive prompt loop
"""
import sys
from qsearch import SemanticSearch, print_hits

COLLECTION = "semantic_search_docs"

# Step 11: varied queries whose wording does NOT keyword-match the documents,
# so any relevance comes from semantic (vector) similarity.
DEMO_QUERIES = [
    "How can I grow my money for retirement?",   # -> finance
    "photos of the early universe",              # -> space
    "keeping your heart healthy",                # -> health
    "making bread at home",                      # -> cooking
    "how do computers understand pictures?",     # -> technology
    "saving the honeybees",                      # -> nature
]


def main():
    ss = SemanticSearch(COLLECTION)

    if len(sys.argv) > 1 and sys.argv[1] == "-i":
        print("Interactive semantic search. Type a query (blank to quit).")
        while True:
            q = input("\nquery> ").strip()
            if not q:
                break
            print_hits(q, ss.search(q, top_k=3))
        return

    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        print_hits(q, ss.search(q, top_k=3))
        return

    for q in DEMO_QUERIES:
        print_hits(q, ss.search(q, top_k=3))


if __name__ == "__main__":
    main()
