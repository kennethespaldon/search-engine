import json 
from pathlib import Path

class IndexReader:
    def __init__(self):
        output = Path("output")

        self.index_file = output/"merged_index.jsonl"

        self.offsets = {}
        with open(output/"term_offsets.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                term, offset = json.loads(line)
                self.offsets[term] = offset

        with open(output/"doc_urls.json", "r", encoding = "utf-8") as f:
            self.doc_urls = json.load(f)

    # Retrieve the posting list for a stemmed term
    def get_postings(self, term):
        offset = self.offsets.get(term)

        # Return an empty list if the term doesn't exist
        if offset is None: 
            return []

        with open(self.index_file, "rb") as f:
            f.seek(offset)
            line= f.readline()

        stored_term, postings = json.loads(line)

        return postings

    def get_url(self, doc_id):
        return self.doc_urls.get(str(doc_id))

if __name__ == "__main__":
    reader = IndexReader()

    print("Posting list for 'machin':")
    print(reader.get_postings("machin")[:3])

    print("URL for document 0:")
    print(reader.get_url(0))

    print("Nonexistent term:")
    print(reader.get_postings("zzzxxyy123"))