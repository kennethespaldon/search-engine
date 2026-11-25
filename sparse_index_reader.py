import bisect
import json
from pathlib import Path

class SparseIndexReader:
    def __init__(self):
        output = Path("output")

        self.index_file = output/"merged_index.jsonl"
        self.lookup_file = output/"term_offsets.jsonl"

        # load only the sparse checkpoints into memory
        self.terms = []
        self.positions = []

        with open(output/ "sparse_offsets.jsonl", "r", encoding = "utf-8") as f: 
            for line in f: 
                term, pos =  json.loads(line)
                self.terms.append(term)
                self.positions.append(pos)

        # load the doc id into URL mapping
        with open(output/ "doc_urls.json", "r", encoding="utf-8") as f: 
            self.doc_urls =json.load(f)

    # Retrieve posting using sparse lookup
    def get_postings(self, term):
        # find the  checkpoint at or before the requested term
        i = bisect.bisect_right(self.terms, term) - 1

        # if checkpoint comes before the first checkpoint , then return []
        if i < 0:
            return []

        # jump to the checkpoint in the lookupfile
        with open(self.lookup_file, "rb") as lookup: 
            lookup.seek(self.positions[i])

            # Scan till the term is found
            while True: 
                line = lookup.readline()

                if not line: 
                    return []

                s_term, index_offset = json.loads(line)

                if s_term == term: 
                    break

                # stop when the term is passed alphabetically
                if s_term > term: 
                    return []

        # Use the offset to retrieve postings from the merged index
        with open(self.index_file, "rb") as fi: 
            fi.seek(index_offset)
            line = fi.readline()

        s_term, postings = json.loads(line)

        # Verify the offset points to correct term
        assert s_term == term, "Incorrect index offset"

        return postings

    # Return the original URL for a document
    def get_url(self, doc_id):
        return self.doc_urls.get(str(doc_id))


if __name__ == "__main__":
    reader = SparseIndexReader()

    print("Checkpoints loaded:", len(reader.terms))
    print("Posting list for 'machin':")
    print(reader.get_postings("machin")[:3])

    print("URL for document 0:")
    print(reader.get_url(0))

    print("Nonexistent term:")
    print(reader.get_postings("zzzxxyy123"))

