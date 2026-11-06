
from collections import defaultdict
from itertools import islice
import json

from document_processor import process_corpus
from disk_indexer import read_partial


# Build the expected index directly from 12 documents
expected = defaultdict(list)

for doc in islice(process_corpus("DEV"), 12):
    for term, stats in doc.terms.items():
        expected[term].append([doc.doc_id,
    stats.tf,
    stats.title,
    stats.heading,
    stats.bold])


# Read the merged index from disk
merged = dict(read_partial("output/merged_index.jsonl"))

# Read the document ID to URL mapping
with open("output/doc_urls.json", encoding="utf-8") as file:
    doc_urls = json.load(file)


# Check that all terms and postings match
assert expected == merged, "Merged index does not match!"
assert len(doc_urls) == 12, "Document count does not match!"

print("Merge validation passed!")
print("Documents:", len(doc_urls))
print("Unique terms:", len(merged))
