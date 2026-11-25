"""
Console search engine over the on-disk inverted index.

Pages that contain every query term are found first. If there are too few,
pages that contain any of the terms are included too.
Query words that aren't in the index are ignored.

Pages are ranked by a tf-idf score that uses BM25 to limit the effect of
repeated words and long pages, with extra weight for terms in titles, headings,
and bold text, and a small preference for pages with shorter URLs.

Run disk_indexer.py, build_lookup.py, and build_sparse_lookup.py before
searching:

    python search.py
"""

import heapq
import json
import math
import re
from array import array
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from nltk.stem import PorterStemmer
from sparse_index_reader import SparseIndexReader
from tokenizer import tokenize

# Bonus for a term that appears at least once in each kind of important text.
# The bonuses are small next to the BM25 weight's limit of K1 + 1, so important
# text helps a page without replacing how well the rest of the page matches.
TITLE_W = 0.5
HEADING_W = 0.25
BOLD_W = 0.1

# BM25 constants. K1 controls how quickly repeating a term stops adding to the
# score. B controls how strongly long pages are penalized (0 = not at all).
K1 = 1.2
B = 0.75

# Largest share of its score that a page can gain for having a short URL.
DEPTH_W = 0.1

INDEX_FILE = Path("output/merged_index.jsonl")
LENGTHS_FILE = Path("output/doc_lengths.json")


def load_doc_lengths(doc_count):
    """
    Returns an array of page lengths (total tokens), indexed by doc ID.

    A page's length is the sum of its tf values. It is computed by reading the
    index one posting list at a time, so the index is never all in memory. The
    result is saved, so later runs skip this unless the index has changed.
    """
    if (LENGTHS_FILE.is_file()
            and LENGTHS_FILE.stat().st_mtime > INDEX_FILE.stat().st_mtime):
        with open(LENGTHS_FILE, encoding="utf-8") as f:
            try:
                lengths = array("Q", json.load(f))
            except (ValueError, TypeError):
                lengths = []  # Damaged file: compute the lengths again
        if len(lengths) == doc_count:
            return lengths

    print("Computing page lengths (first run only)...")
    # Pages with no text have no postings, so their length stays 0.
    lengths = array("Q", [0]) * doc_count
    with open(INDEX_FILE, encoding="utf-8") as f:
        for line in f:
            _, postings = json.loads(line)
            for posting in postings:
                lengths[posting[0]] += posting[1]

    with open(LENGTHS_FILE, "w", encoding="utf-8") as f:
        json.dump(lengths.tolist(), f)
    return lengths


def doc_weight(tf, title, heading, bold, relative_length):
    """
    Returns the weight of a term in a page: BM25 plus important-text bonuses.

    relative_length is the page's length divided by the average length. The
    BM25 part rises with tf but never reaches K1 + 1, so repeating a word many
    times can't dominate. A longer page needs more occurrences to reach the
    same weight.

    The bonuses are added after BM25 so that they aren't flattened by its
    limit. Each is given at most once per term, so repeating a word in bold
    text or headings can't inflate the score.
    """
    length_factor = 1 - B + B * relative_length
    weight = tf * (K1 + 1) / (tf + K1 * length_factor)

    if title:
        weight += TITLE_W
    if heading:
        weight += HEADING_W
    if bold:
        weight += BOLD_W
    return weight


def url_depth(url):
    """
    Returns how deep a URL is: its number of path segments, plus 1 if it has a
    query string. index files don't count, since /a/index.html is the same
    level as /a/. A homepage has depth 0.
    """
    try:
        parts = urlsplit(url)
    except ValueError:
        return url.count("/")  # Malformed URL: use a rough depth
    segments = [segment for segment in parts.path.split("/")
                if segment and not re.fullmatch(r"index\.\w+", segment)]
    return len(segments) + bool(parts.query)


def depth_boost(url):
    """
    Returns the number to multiply a page's score by, based on its URL depth.

    Main pages usually have shorter URLs, so they get a slightly larger boost:
    1.1 for a homepage, then 1.05, 1.033, and so on. It is always above 1 and
    at most 1 + DEPTH_W, so it mostly decides between pages with close scores.
    """
    return 1 + DEPTH_W / (1 + url_depth(url))


class SearchEngine:
    def __init__(self):
        self.reader = SparseIndexReader()
        self.stemmer = PorterStemmer()
        self.doc_count = len(self.reader.doc_urls)
        self.doc_lengths = load_doc_lengths(self.doc_count)
        self.avg_length = sum(self.doc_lengths) / self.doc_count
        # Computed once here because parsing URLs during a search is slow.
        self.depth_boosts = array("d", (
            depth_boost(self.reader.get_url(doc_id))
            for doc_id in range(self.doc_count)))

    def parse_query(self, query):
        """Returns a Counter of stemmed query terms, using the indexer's pipeline."""
        return Counter(self.stemmer.stem(token) for token in tokenize(query))

    def _pages_with_all(self, term_postings):
        """Returns the set of doc IDs that contain every term."""
        # Start from the rarest term so the candidate set stays small.
        terms = sorted(term_postings, key=lambda t: len(term_postings[t]))
        pages = {p[0] for p in term_postings[terms[0]]}
        for term in terms[1:]:
            if not pages:
                break
            pages &= {p[0] for p in term_postings[term]}
        return pages

    def search(self, query, k=10):
        """Returns up to k (url, score) pairs, best first."""
        query_terms = self.parse_query(query)
        if not query_terms:
            return []

        # Words that aren't in the index can't match any page, so ignore them.
        term_postings = {}
        for term in query_terms:
            postings = self.reader.get_postings(term)
            if postings:
                term_postings[term] = postings
        if not term_postings:
            return []

        # Prefer pages with every term (AND). If there are too few to fill the
        # results, use pages with any of the terms instead (OR).
        candidates = self._pages_with_all(term_postings)
        if len(candidates) < k:
            for postings in term_postings.values():
                candidates.update(p[0] for p in postings)

        # Score = sum over query terms of query weight (log qtf * idf)
        # times page weight (BM25 plus bonuses).
        scores = dict.fromkeys(candidates, 0.0)
        for term, postings in term_postings.items():
            idf = math.log10(self.doc_count / len(postings))
            wq = (1 + math.log10(query_terms[term])) * idf
            for doc_id, tf, title, heading, bold in postings:
                if doc_id in scores:
                    relative_length = self.doc_lengths[doc_id] / self.avg_length
                    scores[doc_id] += wq * doc_weight(
                        tf, title, heading, bold, relative_length)

        # Slightly prefer pages with shorter URLs.
        for doc_id in scores:
            scores[doc_id] *= self.depth_boosts[doc_id]

        # Highest score first. Equal scores are ordered by lower doc ID.
        top = heapq.nsmallest(
            k, scores.items(), key=lambda item: (-item[1], item[0]))
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
