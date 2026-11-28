
import time
import tracemalloc

from search import SearchEngine
import os
import psutil

process = psutil.Process(os.getpid())

# Display current process memory usage in MB
def show_memory(label):
    # Measures the amount of process memory currently held in physical RAM and convert into MB
    rss = process.memory_info().rss / (1024 ** 2)
    print(f"{label}: {rss:.2f} MB")

def main():
    # track memory allocations
    tracemalloc.start()

    # Record starting time 
    start = time.perf_counter()

    # Measure process memory before loading index
    show_memory("Before loading index")

    # Load the index reader and search engine
    engine = SearchEngine()

    # Measure process memory after index reader initialized
    show_memory("After loading index")

    # Get the current process and measure its total resident memory
    process = psutil.Process(os.getpid())
    rss_mb = process.memory_info().rss / (1024 ** 2)

    print(f"Process memory (RSS): {rss_mb:.2f} MB")

    # Calculate the total time spent initializing the search engine.
    elapsed = time.perf_counter() - start

    # Retrieve the current and peak Python memory allocations
    # recorded since tracemalloc.start() was called.
    current, peak = tracemalloc.get_traced_memory()

    print(f"Startup time: {elapsed:.2f} seconds")
    print(f"Current Python memory: {current / 1024**2:.2f} MB")
    print(f"Peak Python memory: {peak / 1024**2:.2f} MB")
    with open(engine.reader.lookup_file, "r", encoding="utf-8") as f:
        term_count = sum(1 for _ in f)

    print(f"Terms in lookup: {term_count:,}")
    print(f"Documents: {engine.doc_count:,}")

    tracemalloc.stop()


if __name__ == "__main__":
    main()
