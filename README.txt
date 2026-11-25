SEARCH ENGINE
UCI CS 121 - Information Retrieval, Assignment 3
Godspeed - Harry Lwin, Kenneth Espaldon, Gerome Monforte Fevidal

OVERVIEW
This project builds a disk-based inverted index from the DEV web-page corpus
and provides a command-line search engine. Search uses Boolean AND matching
and ranks matching documents with term frequency, inverse document frequency,
and additional weight for terms found in titles, headings, and bold text.

The optimized reader uses a sparse lookup: it keeps every 256th term as a
checkpoint in memory and reads the remaining lookup entries from disk.

REQUIREMENTS
- Python 3
- beautifulsoup4
- lxml
- nltk

Install the required packages:

    python -m pip install beautifulsoup4 lxml nltk

For the optional performance comparison script, also install psutil:

    python -m pip install psutil

DATASET
Place the provided DEV folder in the project directory, next to
'disk_indexer.py'. For example:

    search-engine/
        DEV/
        disk_indexer.py
        build_lookup.py
        build_sparse_lookup.py
        sparse_index_reader.py
        search.py

BUILDING THE INDEX
Run these commands in order from the project directory:

    python disk_indexer.py
    python build_lookup.py
    python build_sparse_lookup.py

1. disk_indexer.py creates partial inverted indexes and merges them into
   output/merged_index.jsonl. It also writes output/doc_urls.json.
2. build_lookup.py creates output/term_offsets.jsonl, which records each term
   and the byte offset of its posting list in the merged index.
3. build_sparse_lookup.py creates output/sparse_offsets.jsonl, retaining a
   checkpoint for every 256 terms to reduce memory usage during search.

The output/ folder contains generated index files. If these files are not
included with the submission, run the three build commands before searching.

INDEX STATISTICS
To display document counts, unique-term counts, and index size, run:

    python index_stats.py

SEARCHING
After building the index, start the search prompt:

    python search.py

Type a query and press Enter. The program returns up to 10 matching URLs,
ranked by relevance. Enter an empty query or type 'quit' to exit.

The final search.py should use SparseIndexReader from
sparse_index_reader.py so that the sparse lookup is used during searches.

PERFORMANCE AND TESTING (OPTIONAL)
If the corresponding test scripts are included, run:

    python test_sparse_reader.py
    python compare_performance.py original
    python compare_performance.py sparse

The correctness test compares posting lists returned by the original and
sparse readers. The performance script measures memory use, startup time,
and query-response times separately for each reader.

NOTES
- Run all commands from the project's root directory.
- Index generation may take time on the full DEV corpus.
- The index is stored on disk rather than loaded entirely into RAM.