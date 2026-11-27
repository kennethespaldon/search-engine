import json
from pathlib import Path

# Calculate page ranking using Algebraic PageRank Formula
def calculate_page_ranking( max_iter = 100, tolerance = 1e-6 , d = 0.85):
    with open("output/doc_urls.json", "r", encoding = "utf-8") as f: 
        n = len(json.load(f))

    graph = [[] for _ in range(n)]

    # Create a link graph from page_links.jsonl
    with open("output/page_links.jsonl", "r", encoding = "utf-8") as f: 
        for line in f: 
            doc_id , outgoing = json.loads(line)
            graph[doc_id] = outgoing

    # initialize all ranks with 1.0
    ranks= [1.0] * n

    # Update the ranks until they converge or reach maximum iteration limit
    for iteration in range(max_iter):

        # find total rank of pages that have no outgoing links
        dangling_rank = sum(ranks[i]  for i in range(n) if not graph[i])

        # give every page a base rank and distribute dangling rank evenly
        base = (1-d) + d * dangling_rank/n
        new_ranks = [base] * n
        
        # each page distributes its rank equally among its outgoing links
        for page, outgoing in enumerate(graph):
            if not outgoing: 
                continue

            contribution = d * ranks[page] / len(outgoing)

            # Add the contributon to each linked page's score
            for target in outgoing: 
                new_ranks[target] += contribution

        # Measure the average change in rank between iterations
        difference = sum(
            abs(new_ranks[i] - ranks[i]) for i in range(n)
        ) / n

        # Replace previous score with new one
        ranks = new_ranks

        # Stop if the average change is smaller than the tolerance
        if difference< tolerance:
            print("Coverged after ", iteration + 1, " iterations")
            break

    output =  Path("output/page_rank.json")

    # Save the ranks to the page_rank.json
    with open(output, "w", encoding = "utf-8") as f: 
        json.dump(ranks, f)

    print("Page Rank saved")
    print("Pages ranked: ", n)

if __name__ == "__main__":
    calculate_page_ranking()

