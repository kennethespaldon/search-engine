from collections import defaultdict
from itertools import islice
import json
from pathlib import Path

from document_processor import process_corpus

def build_index(root, limit = 5) :
    index = defaultdict(list)
    doc_urls  = {}


    for doc in islice(process_corpus(root), limit) :
        doc_urls[doc.doc_id] = doc.url

        for term, stats in doc.terms.items():
            index[term].append((doc.doc_id, stats.tf))

    return index, doc_urls

def save_index (index, doc_urls):
    output = Path("output")

    output.mkdir(exist_ok=True)

    with open(output/"index.json", "w", encoding="utf-8") as f: 
        json.dump(index, f)

    with open(output/"doc_url.json", "w", encoding="utf-8") as d:
        json.dump(doc_urls, d)

    size = (output / "index.json").stat().st_size / 1024

    print(f"Index size: {size:.2f} KB")



if __name__ == "__main__":
    index, doc_urls = build_index("DEV")

    print("Documents indexed:", len(doc_urls))
    print("Unique terms:", len(index))

    save_index(index, doc_urls)

