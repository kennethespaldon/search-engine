"""
Console search engine over the on-disk inverted index.

Queries are boolean AND: a page must contain every query term. Matching pages
are ranked by a tf-idf score, with extra weight for terms in titles,
headings, and bold text.

Run disk_indexer.py and then build_lookup.py before searching:

    python search.py
"""

import heapq
import math
from collections import Counter

from nltk.stem import PorterStemmer

from index_reader import IndexReader
from tokenizer import tokenize

# Extra weight given to an occurrence inside important text, on top of the
# 1 it already counts toward tf. One occurrence can count toward several.
TITLE_W = 2.0
HEADING_W = 1.5
BOLD_W = 0.5


def doc_weight(tf, title, heading, bold):
    """
    Returns the weight of a term in a page: log of the boosted tf.

    Occurrences in titles, headings, and bold text are boosted before the
    log is taken, so important words count for more.
    """
    weighted_tf = tf + TITLE_W * title + HEADING_W * heading + BOLD_W * bold
    return 1 + math.log10(weighted_tf)


class SearchEngine:
    def __init__(self):
        self.reader = IndexReader()
        self.stemmer = PorterStemmer()
        self.doc_count = len(self.reader.doc_urls)

    def parse_query(self, query):
        """Returns a Counter of stemmed query terms, using the indexer's pipeline."""
        return Counter(self.stemmer.stem(token) for token in tokenize(query))

    def search(self, query, k=10):
        """Returns up to k (url, score) pairs, best first."""
        query_terms = self.parse_query(query)
        if not query_terms:
            return []

        term_postings = {}
        for term in query_terms:
            postings = self.reader.get_postings(term)
            if not postings:
                return []  # AND: a missing term means no page has every term
            term_postings[term] = postings

        # Intersect starting from the rarest term so the candidate set stays small.
        terms = sorted(term_postings, key=lambda t: len(term_postings[t]))
        candidates = {p[0] for p in term_postings[terms[0]]}
        for term in terms[1:]:
            candidates &= {p[0] for p in term_postings[term]}
            if not candidates:
                return []

        # Score = sum over query terms of query weight (log qtf * idf)
        # times page weight (log boosted tf).
        scores = dict.fromkeys(candidates, 0.0)
        for term in terms:
            idf = math.log10(self.doc_count / len(term_postings[term]))
            wq = (1 + math.log10(query_terms[term])) * idf
            for doc_id, tf, title, heading, bold in term_postings[term]:
                if doc_id in scores:
                    scores[doc_id] += wq * doc_weight(tf, title, heading, bold)

        top = heapq.nlargest(k, scores.items(), key=lambda item: item[1])
        return [(self.reader.get_url(doc_id), score) for doc_id, score in top]


def main():
    print("Loading index...")
    engine = SearchEngine()
    print("Ready. Press Enter on an empty line or type 'quit' to exit.")

    while True:
        try:
            query = input("\nSearch: ").strip()
        except EOFError:
            break
        if not query or query.lower() == "quit":
            break

        results = engine.search(query)

        if not results:
            print("No results.")
        for rank, (url, score) in enumerate(results, 1):
            print(f"{rank:2}. {url}")


if __name__ == "__main__":
    main()
