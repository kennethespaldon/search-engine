from collections import defaultdict
from itertools import islice
from pathlib import Path
import json
import heapq

from document_processor import process_corpus

def write_partial (index, fileName) : 
    with open(fileName, "w", encoding="utf-8") as f: 
        for term in sorted(index):
            postings  = index[term]
            f.write(json.dumps([term, postings]) + "\n")


def read_partial (fileName): 
    with open(fileName, "r", encoding="utf-8") as f: 
        for line in f: 
            term, postings = json.loads(line)
            yield term, postings

def merge_partials ():
    folder = Path("output/partials") 
    files = sorted(folder.glob("partial_*.jsonl"))

    if not files: 
        print("No partial indexes found")
        return

    streams = [read_partial(file) for file in files]

    merged = heapq.merge(*streams, key = lambda item: item[0])

    curr_term = None
    curr_postings = []
    uniq_terms = 0

    with open("output/merged_index.jsonl", "w", encoding="utf-8") as output: 
        for term, postings in merged: 
            if curr_term is not None and term != curr_term:
                output.write(json.dumps([curr_term, curr_postings]) + "\n")
                uniq_terms +=1
                curr_postings = []

            curr_term = term
            curr_postings.extend(postings)

        if curr_term is not None: 
            output.write(json.dumps([curr_term, curr_postings]) + "\n")
            uniq_terms += 1

    print("Partial indexes merged")
    print("Unique terms: ", uniq_terms)


def build_partial (root, size = 5, limit = 12) :
    output = Path("output/partials")

    output.mkdir(parents=True, exist_ok=True)

    index = defaultdict(list)
    partial_count =0
    doc_count = 0
    doc_urls = {}


    for doc in islice(process_corpus(root), limit) :
        doc_count += 1
        doc_urls[doc.doc_id] = doc.url

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

    with open(output.parent/"doc_urls.json", "w", encoding="utf-8") as f: 
        json.dump(doc_urls, f)

    print("Documents Processed: ", doc_count)
    print("Partial indexes processed: ", partial_count)

if __name__ == "__main__":
    build_partial("DEV", size=5, limit=12)
    merge_partials()


