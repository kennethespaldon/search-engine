from collections import defaultdict
from itertools import islice
import json
from pathlib import Path

from document_processor import process_corpus

# Build inverted index from processed  documents
def build_index(root, limit = 5) :
    # store each term with its list of document IDs and frequencies
    index = defaultdict(list)

    # map documents IDs to their original URLs
    doc_urls  = {}

    # Process only the first 5 documents 
    for doc in islice(process_corpus(root), limit) :
        doc_urls[doc.doc_id] = doc.url

        # Add a posting for each term in the document
        for term, stats in doc.terms.items():
            index[term].append((doc.doc_id, stats.tf))

    return index, doc_urls

# Save the inverted index and document URLs to the disk
def save_index (index, doc_urls):
    output = Path("output")

    # Create the output folder if not existed
    output.mkdir(exist_ok=True)

    # Save each term and its posting list as JSON
    with open(output/"index.json", "w", encoding="utf-8") as f: 
        json.dump(index, f)

    # Save the mapping between document IDs and URLs
    with open(output/"doc_url.json", "w", encoding="utf-8") as d:
        json.dump(doc_urls, d)

    # Calculate the index file size in KB
    size = (output / "index.json").stat().st_size / 1024

    print(f"Index size: {size:.2f} KB")



if __name__ == "__main__":
    index, doc_urls = build_index("DEV")

    print("Documents indexed:", len(doc_urls))
    print("Unique terms:", len(index))

    save_index(index, doc_urls)

