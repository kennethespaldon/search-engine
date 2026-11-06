from collections import defaultdict
from itertools import islice
from pathlib import Path
import json

from document_processor import process_corpus

def write_partial (index, fileName) : 
    with open(fileName, "w", encoding="utf-8") as f: 
        for term in sorted(index):
            postings  = index[term]
            f.write(json.dumps([term, postings]) + "\n")


def build_partial (root, size = 5, limit = 12) :
    output = Path("output/partials")

    output.mkdir(parents=True, exist_ok=True)

    index = defaultdict(list)
    partial_count =0
    doc_count = 0


    for doc in islice(process_corpus(root), limit) :
        doc_count += 1

        for term, stats in doc.terms.items():
            index[term].append((doc.doc_id, stats.tf))


        if doc_count % size == 0:
            partial_count += 1

            fileName = output / f"partial_{partial_count: 03d}.jsonl"

            write_partial(index, fileName)

            print(f"Saved {fileName}")

            index.clear()

    if index: 
        partial_count += 1

        fileName = output/ f"partial_{partial_count: 03d}.jsonl"

        write_partial(index, fileName)
        print(f"Saved {fileName}")

    print("Documents Processed: ", doc_count)
    print("Partial indexes processed: ", partial_count)

if __name__ == "__main__":
    build_partial("DEV", size=5, limit=12)


