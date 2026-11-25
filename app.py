from time import perf_counter
from flask import Flask, render_template, request, jsonify
from search import SearchEngine

app = Flask(__name__)

engine= SearchEngine()

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/search")
def api_search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify(query = "", results=[], count = 0, elapsed_ms = 0.0)

    start = perf_counter()

    try:
        hits = engine.search(query, k = 10)
    except Exception: 
        app.logger.exception("Search failed")
        return jsonify(error = "Search failed. Check the server termnal. "), 500

    elapsed_ms = round((perf_counter() - start) * 1000, 2)
    results = [{
        "url" : url, 
        "score": round(float(score), 4)} for url, score in hits
    ]

    return jsonify(
        query = query, 
        results = results, 
        count = len(results), 
        elapsed_ms = elapsed_ms
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
