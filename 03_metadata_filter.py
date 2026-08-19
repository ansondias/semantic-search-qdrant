"""
Step 12: Metadata filtering.

Qdrant can combine vector similarity with structured payload filters, so you
retrieve the semantically closest documents *within* a subset (e.g. only the
'nature' category, or only documents from 2020 onward).

Run:  python 03_metadata_filter.py
"""
from qsearch import SemanticSearch, print_hits

COLLECTION = "semantic_search_docs"


def main():
    ss = SemanticSearch(COLLECTION)

    query = "living things under threat from a warming planet"

    # (a) unfiltered - searches the whole corpus
    print_hits(query, ss.search(query, top_k=3), note="no filter")

    # (b) filter: only documents in the 'nature' category
    print_hits(query,
               ss.search(query, top_k=3,
                         query_filter=ss.category_filter("nature")),
               note="category == nature")

    # (c) filter: only documents published in 2020 or later
    print_hits(query,
               ss.search(query, top_k=3,
                         query_filter=ss.year_gte_filter(2020)),
               note="year >= 2020")


if __name__ == "__main__":
    main()
