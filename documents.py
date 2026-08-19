"""
Step 2: Prepare a collection of text documents.

A small, deliberately diverse corpus spanning several topics (space, cooking,
finance, health, technology, sports, nature). Each document carries metadata
(category, author, year) so we can demonstrate metadata filtering later.
The topical spread makes semantic relevance easy to see: a query about
"how to invest money" should surface the finance docs, not the cooking ones,
even when no keyword overlaps.
"""

DOCUMENTS = [
    {
        "text": "The James Webb Space Telescope captures infrared images of distant "
                "galaxies formed shortly after the Big Bang, revealing details never seen before.",
        "category": "space", "author": "NASA", "year": 2022,
    },
    {
        "text": "Black holes are regions of spacetime where gravity is so strong that "
                "not even light can escape their event horizon.",
        "category": "space", "author": "S. Hawking", "year": 1988,
    },
    {
        "text": "To make a fluffy omelette, whisk the eggs vigorously, cook on low heat, "
                "and fold gently before the center fully sets.",
        "category": "cooking", "author": "J. Child", "year": 2001,
    },
    {
        "text": "Sourdough bread relies on a natural starter of wild yeast and bacteria, "
                "giving the loaf its tangy flavor and chewy crust.",
        "category": "cooking", "author": "P. Hollywood", "year": 2018,
    },
    {
        "text": "Diversifying your portfolio across stocks, bonds, and index funds reduces "
                "risk and smooths returns over the long term.",
        "category": "finance", "author": "B. Graham", "year": 1949,
    },
    {
        "text": "Compound interest allows your savings to grow exponentially, as the returns "
                "themselves begin to earn additional returns over time.",
        "category": "finance", "author": "W. Buffett", "year": 2005,
    },
    {
        "text": "Regular aerobic exercise strengthens the heart, lowers blood pressure, and "
                "improves overall cardiovascular health.",
        "category": "health", "author": "WHO", "year": 2020,
    },
    {
        "text": "A balanced diet rich in vegetables, whole grains, and lean protein supports "
                "immune function and sustained energy.",
        "category": "health", "author": "Harvard Health", "year": 2019,
    },
    {
        "text": "Neural networks learn hierarchical representations of data, enabling machines "
                "to recognize images, translate languages, and generate text.",
        "category": "technology", "author": "Y. LeCun", "year": 2015,
    },
    {
        "text": "Vector databases store high-dimensional embeddings and use approximate nearest "
                "neighbor search to power semantic retrieval at scale.",
        "category": "technology", "author": "Qdrant", "year": 2023,
    },
    {
        "text": "Lionel Messi dribbled past three defenders and curled the ball into the top "
                "corner to win the match in stoppage time.",
        "category": "sports", "author": "FIFA", "year": 2022,
    },
    {
        "text": "Marathon runners train for months, gradually increasing mileage to build the "
                "endurance needed to finish 42 kilometers.",
        "category": "sports", "author": "IAAF", "year": 2017,
    },
    {
        "text": "Coral reefs are among the most biodiverse ecosystems on Earth, but rising ocean "
                "temperatures cause widespread coral bleaching.",
        "category": "nature", "author": "NOAA", "year": 2021,
    },
    {
        "text": "Bees pollinate a third of the crops humans eat, making their decline a serious "
                "threat to global food security.",
        "category": "nature", "author": "Greenpeace", "year": 2016,
    },
]
