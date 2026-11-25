import json 
from pathlib import Path

# Build sparse lookup by only storing only every 256th term. 
def build_sparse_lookup(step = 256):
    src = Path("output/term_offsets.jsonl")
    des = Path("output/sparse_offsets.jsonl")

    term_count = 0
    checkpoint_count = 0

    with open(src, "rb") as lookup, open(des, "w", encoding = "utf-8") as sparse:
        while True:
            # Records the byte position where the current line starts
            pos = lookup.tell()

            # Read the next term and offset stored in the lookup file
            line = lookup.readline()

            # Stop when there are no more lines to read
            if not line:
                break

            # Save only every 256th term as checkpoint
            if term_count % step == 0:
                # Extract term and offset in the merged index
                term, offset = json.loads(line)

                sparse.write(json.dumps([term, pos]) + "\n")

                checkpoint_count += 1

            term_count += 1

        print("Term processed: ", term_count)
        print("Checkpoints processed: ", checkpoint_count)

if __name__ == "__main__":
    build_sparse_lookup()


