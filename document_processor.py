"""
Turns corpus pages into per-document term data for the inverted index.

This is the interface between document processing and index construction:

    for doc in process_corpus("DEV"):
        for term, stats in doc.terms.items():
            ...  # build a posting using doc.doc_id, stats.tf, etc.
"""

from dataclasses import dataclass

from nltk.stem import PorterStemmer

from corpus import iter_documents
from html_extractor import BOLD, HEADING, TITLE, extract_text_segments
from tokenizer import tokenize

_stemmer = PorterStemmer()


@dataclass
class TermStats:
    """
    How often one stemmed term appears in one document.

    tf counts every occurrence once. The other fields count the occurrences
    inside important text, and one occurrence can count toward several of them.
    """
    tf: int = 0
    title: int = 0
    heading: int = 0
    bold: int = 0


@dataclass
class ProcessedDocument:
    """A document's URL and terms, ready to be added to an index."""
    doc_id: int
    url: str
    terms: dict[str, TermStats]


def process_document(document):
    """
    Returns the ProcessedDocument for a corpus Document.

    All tokens are kept, including stop words, as the assignment requires.
    """
    terms = {}

    for text, fields in extract_text_segments(document.content):
        for token in tokenize(text):
            term = _stemmer.stem(token)
            stats = terms.setdefault(term, TermStats())

            stats.tf += 1
            stats.title += TITLE in fields
            stats.heading += HEADING in fields
            stats.bold += BOLD in fields

    return ProcessedDocument(document.doc_id, document.url, terms)


def process_corpus(root):
    """
    Yields a ProcessedDocument for each page under root.

    This is a generator, so only one document is held in memory at a time and
    the indexer can decide when to flush its index to disk.
    """
    for document in iter_documents(root):
        yield process_document(document)
