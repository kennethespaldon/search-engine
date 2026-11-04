"""Reads the crawled pages in the corpus folder, one document at a time."""

import json
import logging
import os
from dataclasses import dataclass
from urllib.parse import urldefrag

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """One unique web page from the corpus, before any text processing."""
    doc_id: int
    url: str
    content: str


def _json_paths(root):
    """
    Yields the path of every JSON file under root in a fixed order.

    os.walk() returns folders in an arbitrary order that can differ between
    machines. Sorting keeps doc IDs the same on every run and for every
    teammate.
    """
    for folder, subfolders, filenames in os.walk(root):
        subfolders.sort()
        for filename in sorted(filenames):
            if filename.endswith(".json"):
                yield os.path.join(folder, filename)


def _read_page(path):
    """
    Returns the (url, content) stored in a JSON file.

    Raises OSError or ValueError if the file can't be read or doesn't have
    the expected fields. UnicodeDecodeError and JSONDecodeError are both
    subclasses of ValueError.
    """
    with open(path, encoding="utf-8") as file:
        page = json.load(file)

    if not isinstance(page, dict):
        raise ValueError("expected a JSON object")

    url = page.get("url")
    content = page.get("content")
    if not isinstance(url, str) or not url or not isinstance(content, str):
        raise ValueError("missing a valid url or content field")

    return url, content


def iter_documents(root):
    """
    Yields a Document for each unique page under root.

    There is one folder per domain and each JSON file is one web page. URL
    fragments are removed because they only point to a location inside a page.
    Files whose URLs match after that are the same page, so only the first is
    kept and search results can't list the same URL twice.

    Only documents that are yielded receive a doc ID, so IDs have no gaps.
    Files that can't be used are logged and skipped so that one bad file
    doesn't stop a long indexing run.
    """
    seen_urls = set()
    doc_id = 0

    for path in _json_paths(root):
        try:
            url, content = _read_page(path)
        except (OSError, ValueError) as error:
            logger.warning("Skipping %s: %s", path, error)
            continue

        url = urldefrag(url).url
        if url in seen_urls:
            continue
        seen_urls.add(url)

        yield Document(doc_id, url, content)
        doc_id += 1
