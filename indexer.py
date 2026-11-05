from collections import defaultdict
from itertools import islice

from document_processor import process_corpus

def build_index(root, limit = 5) :
    index = defaultdict(list)
    doc_urls  = {}


    for doc in islice(process_corpus(root), limit) :
        doc_urls[doc.doc_id] = doc.url

        for term, stats in doc.terms.items():
            index[term].append((doc.doc_id, stats.tf))

    return index, doc_urls


if __name__ == "__main__":
    index, doc_urls = build_index("DEV")

    print("Documents indexed:", len(doc_urls))
    print("Unique terms:", len(index))

    for term in list(index)[:10]:
        print(term, index[term])

