import json 
from pathlib import Path

# Build a lookup that maps each term to its position in the index file
def build_lookup():
    index_file = Path("output/merged_index.jsonl")
    lookup_file = Path("output/term_offsets.jsonl")

    if not index_file.is_file():
        print("Merge index file not found")
        return

    term_count = 0

    # Read the index file in bytes and write into lookup file
    with open(index_file, "rb") as index, open(lookup_file, "w", encoding="utf-8") as lookup:
        while True:
            offset = index.tell()

            line = index.readline()

            if not line:
                break

            # Read the term from the index record
            term, postings = json.loads(line)

            # Save the term and its byte offset
            lookup.write(json.dumps([term, offset]) + "\n")

            term_count+=1

    print("Lookup created ")
    print("Terms indexed ", term_count)


if __name__ == "__main__":
    build_lookup()

