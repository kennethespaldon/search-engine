import json
from pathlib import Path
from urllib.parse import urljoin, urldefrag

from bs4 import BeautifulSoup, SoupStrainer
from corpus import iter_documents

def build_link_graph():
    # load doc IDs and their urls from existing index
    with open("output/doc_urls.json", "r", encoding="utf-8") as f:
        doc_urls = {
            int(doc_id) : url for doc_id, url in json.load(f).items()
        }

    # Reverse the mapping 
    url_to_id = {
        url: doc_id for doc_id, url in doc_urls.items()
    }

    output = Path("output/page_links.jsonl")

    page_count = 0
    link_count =0

    with open(output, "w", encoding="utf-8") as f:
        for doc in iter_documents("DEV"):
            # making sure doc IDs match the original index
            if doc_urls.get(doc.doc_id) != doc.url:
                raise ValueError(f"Document ID mismatch: {doc.doc_id}")

            outgoing = set()

            # Parse only anchor tags 
            soup = BeautifulSoup(doc.content, "lxml", parse_only=SoupStrainer("a"))

            for link in soup.find_all("a", href=True):
                href = link["href"].strip()

                if not href:
                    continue

                # Convert relative urls to full urls and remove fragments     
                try:
                    target_url = urldefrag(urljoin(doc.url, href)).url
                except ValueError:
                    continue

                # keeping only links to pages that exists in our index
                target_id = url_to_id.get(target_url)

                if target_id is not None and target_id != doc.doc_id:
                    outgoing.add(target_id)


            f.write(json.dumps([doc.doc_id, sorted(outgoing)]) + "\n")

            page_count+=1
            link_count += len(outgoing)

    # Check if every indexed documents was included in the graph
    if page_count != len(doc_urls):
        raise ValueError("Corpus and index counts do not match")

    print("Pages processed:", page_count)
    print("Internal links found:", link_count)
    print("Graph saved:", output)


if __name__ == "__main__":
    build_link_graph() 