import json
from pathlib import Path

def calculate_index_stats():
    index_file = Path("output/merged_index.jsonl")
    urls_file = Path("output/doc_urls.json")

    if not index_file.is_file() or not urls_file.is_file():
        print("Index files not found. Run disk_indexer.py first.")
        return

    # Get the number of documents from the saved URLs
    with open(urls_file, "r", encoding="utf-8") as file:
        doc_urls = json.load(file)
        document_count = len(doc_urls)

    # Count each line since every line contains one unique term
    with open(index_file, "r", encoding="utf-8") as file:
        unique_terms = sum(1 for line in file)

    # Get the file sizes in bytes and convert them to KB
    index_bytes = index_file.stat().st_size
    urls_bytes = urls_file.stat().st_size

    print(f"Documents indexed: {document_count:,}")
    print(f"Unique terms: {unique_terms:,}")
    print(f"Merged index size: {index_bytes / 1024:,.2f} KB")
    print(f"Total index storage: {(index_bytes + urls_bytes) / 1024:,.2f} KB")

if __name__ == "__main__":
    calculate_index_stats()
