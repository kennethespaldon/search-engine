
import time
import statistics

from search import SearchEngine


# Queries used to measure search performance
QUERIES = [
    "cristina lopes",
    "machine learning",
    "ACM",
    "master of software engineering",
    "uci",
    "computer science",
    "artificial intelligence",
    "research"
]


def benchmark(engine, query, runs=5):
    times = []

    engine.search(query)

    for _ in range(runs):
        start = time.perf_counter()

        results = engine.search(query)

        elapsed = time.perf_counter() - start

        # Convert seconds into milliseconds
        times.append(elapsed * 1000)

    return (
        len(results),
        statistics.median(times),
        max(times)
    )


def main():
    print("Loading search engine...")
    engine = SearchEngine()

    print("\nQuery Performance:\n")

    for query in QUERIES:
        count, median_ms, max_ms = benchmark(engine, query)

        print(f"Query: {query}")
        print(f"Results displayed: {count}")
        print(f"Median time: {median_ms:.2f} ms")
        print(f"Slowest time: {max_ms:.2f} ms")
        print("---------------------------")


if __name__ == "__main__":
    main()
