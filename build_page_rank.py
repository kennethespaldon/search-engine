import json
from pathlib import Path

def calculate_page_ranking( max_iter = 100, tolerance = 1e-6 , d = 0.85):
    with open("output/doc_urls.json", "r", encoding = "utf-8") as f: 
        n = len(json.load(f))

    graph = [[] for _ in range(n)]

    with open("output/page_links.jsonl", "r", encoding = "utf-8") as f: 
        for line in f: 
            doc_id , outgoing = json.loads(line)
            graph[doc_id] = outgoing

    ranks= [1.0] * n

    for iteration in range(max_iter):
        dangling_rank = sum(ranks[i]  for i in range(n) if not graph[i])

        base = (1-d) + d * dangling_rank/n
        new_ranks = [base] * n

        for page, outgoing in enumerate(graph):
            if not outgoing: 
                continue

            contribution = d * ranks[page] / len(outgoing)

            for target in outgoing: 
                new_ranks[target] += contribution

        difference = sum(
            abs(new_ranks[i] - ranks[i]) for i in range(n)
        ) / n

        ranks = new_ranks

        if difference< tolerance:
            print("Coverged after ", iteration + 1, " iterations")
            break

    output =  Path("output/page_rank.json")

    with open(output, "w", encoding = "utf-8") as f: 
        json.dump(ranks, f)

    print("Page Rank saved")
    print("Pages ranked: ", n)

if __name__ == "__main__":
    calculate_page_ranking()

