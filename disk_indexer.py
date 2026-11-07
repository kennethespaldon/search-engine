from collections import defaultdict
from itertools import islice
from pathlib import Path
import json
import heapq
from document_processor import process_corpus

# Save a partial index with terms sorted alphabetically 
def write_partial (index, fileName) : 
    with open(fileName, "w", encoding="utf-8") as f: 
        for term in sorted(index):
            postings  = index[term]
            #store each terms and its posting list 
            f.write(json.dumps([term, postings]) + "\n")

# Read a partial index one term at a time
def read_partial (fileName): 
    with open(fileName, "r", encoding="utf-8") as f: 
        for line in f: 
            term, postings = json.loads(line)
            yield term, postings

# Combine all partial indexes into one final index
def merge_partials ():
    folder = Path("output/partials") 
    files = sorted(folder.glob("partial_*.jsonl"))

    if not files: 
        print("No partial indexes found")
        return

    # Create a generator for each partial index
    streams = [read_partial(file) for file in files]

    # Merge the sorted files in alphabetical order by term
    merged = heapq.merge(*streams, key = lambda item: item[0])

    curr_term = None
    curr_postings = []
    uniq_terms = 0

    with open("output/merged_index.jsonl", "w", encoding="utf-8") as output: 
        for term, postings in merged: 

            # Write previous term once all its postings are collected
            if curr_term is not None and term != curr_term:
                output.write(json.dumps([curr_term, curr_postings]) + "\n")
                uniq_terms +=1
                curr_postings = []

            curr_term = term

            # Combine postings for the same term from different files
            curr_postings.extend(postings)

        #  Write the last term since there  is no next term to trigger it
        if curr_term is not None: 
            output.write(json.dumps([curr_term, curr_postings]) + "\n")
            uniq_terms += 1

    print("Partial indexes merged")
    print("Unique terms: ", uniq_terms)

# Build smaller indexes in batches instead of keeping everything in memory
def build_partial (root, size = 5, limit = 12) :
    output = Path("output/partials")

    # Remove the partial files from previous run if they exists
    for old_file in output.glob("partial_*.jsonl"):
        old_file.unlink()

    # Create the output directory if it doesn't exist
    output.mkdir(parents=True, exist_ok=True)

    index = defaultdict(list)
    partial_count =0
    doc_count = 0
    doc_urls = {}

    for doc in islice(process_corpus(root), limit) :
        doc_count += 1

        # Store the original URL for each document ID
        doc_urls[doc.doc_id] = doc.url

        # Add each term's document ID and frequency to its posting list
        for term, stats in doc.terms.items():
            index[term].append((doc.doc_id,
                                stats.tf,
                                stats.title,
                                stats.heading,
                                stats.bold))

        # Save the current index when a batch is completed
        if doc_count % size == 0:
            partial_count += 1

            fileName = output / f"partial_{partial_count: 03d}.jsonl"

            write_partial(index, fileName)

            print(f"Saved {fileName}")

            # Clear the saved postings to save memory
            index.clear()

    # Save the remaining documents that didn't fill a complete batch
    if index: 
        partial_count += 1

        fileName = output/ f"partial_{partial_count: 03d}.jsonl"

        write_partial(index, fileName)
        print(f"Saved {fileName}")

    # Save the document ID to URL mapping for future search results
    with open(output.parent/"doc_urls.json", "w", encoding="utf-8") as f: 
        json.dump(doc_urls, f)

    print("Documents Processed: ", doc_count)
    print("Partial indexes processed: ", partial_count)

    

if __name__ == "__main__":
    build_partial("DEV", size=5000, limit=None)
    merge_partials()


