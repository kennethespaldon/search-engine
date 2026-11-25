// Frontend for the real Flask /api/search endpoint.
// No sample search index: results come from your Python SearchEngine.

const app = document.getElementById("app");
const form = document.getElementById("form");
const input = document.getElementById("q");
const list = document.getElementById("list");
const meta = document.getElementById("meta");
const themeToggle = document.getElementById("themeToggle");
const searchButton = form.querySelector('button[type="submit"]');
const searchUrl = app.dataset.searchUrl;

let activeRequest = null;

function setLoading(loading) {
  searchButton.disabled = loading;
  searchButton.textContent = loading ? "Searching…" : "Search";
  form.setAttribute("aria-busy", String(loading));
}

function showMessage(title, message) {
  list.replaceChildren();
  const panel = document.createElement("div");
  panel.className = "empty";
  const symbol = document.createElement("div");
  symbol.className = "empty-symbol";
  symbol.setAttribute("aria-hidden", "true");
  symbol.textContent = "⌕";
  const heading = document.createElement("h3");
  heading.textContent = title;
  const description = document.createElement("p");
  description.textContent = message;
  panel.append(symbol, heading, description);
  list.append(panel);
}

function validWebUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:" ? url : null;
  } catch {
    return null;
  }
}

// The Python engine currently returns URLs and scores, not page titles or
// snippets. We display the actual URL rather than inventing page metadata.
function showResults(results) {
  list.replaceChildren();

  for (const [index, result] of results.entries()) {
    const url = validWebUrl(result.url);
    if (!url) continue;

    const article = document.createElement("article");
    article.className = "result";

    const headingRow = document.createElement("div");
    headingRow.className = "result-heading";

    const domain = document.createElement("div");
    domain.className = "domain";
    const domainIcon = document.createElement("span");
    domainIcon.className = "domain-icon";
    domainIcon.setAttribute("aria-hidden", "true");
    domainIcon.textContent = "↗";
    const hostname = document.createElement("span");
    hostname.textContent = url.hostname;
    domain.append(domainIcon, hostname);

    const rank = document.createElement("span");
    rank.className = "rank";
    rank.textContent = `#${index + 1}`;
    headingRow.append(domain, rank);

    const title = document.createElement("h3");
    const anchor = document.createElement("a");
    anchor.href = url.href;
    anchor.target = "_blank";
    anchor.rel = "noopener noreferrer";

    anchor.textContent = url.pathname === "/"
      ? `${url.hostname} — Home page`
      : `${url.hostname}${url.pathname}`;
    title.append(anchor);

    const description = document.createElement("p");
    const score = Number(result.score);
    description.textContent = Number.isFinite(score)
      ? `Relevance score: ${score.toFixed(3)}`
      : "Indexed page";

    const urlText = document.createElement("div");
    urlText.className = "url";
    urlText.textContent = url.href;

    article.append(headingRow, title, description, urlText);
    list.append(article);
  }

  if (!list.childElementCount) {
    showMessage("No valid result links", "The search returned no usable web URLs.");
  }
}

async function run(query) {
  query = query.trim();
  if (!query) { input.focus(); return; }

  if (activeRequest) activeRequest.abort();
  const controller = new AbortController();
  activeRequest = controller;
  app.classList.add("has-results");
  input.value = query;
  setLoading(true);
  meta.textContent = "Searching your index…";
  list.replaceChildren();

  const pageUrl = new URL(window.location.href);
  pageUrl.searchParams.set("q", query);
  window.history.replaceState(null, "", pageUrl);

  try {
    const response = await fetch(`${searchUrl}?${new URLSearchParams({q: query})}`, {
      signal: controller.signal,
      headers: {"Accept": "application/json"}
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `Server returned ${response.status}`);

    const found = Array.isArray(data.results) ? data.results : [];
    const elapsed = Number(data.elapsed_ms);
    const elapsedLabel = Number.isFinite(elapsed) ? `${elapsed.toFixed(2)} ms` : "time unavailable";
    meta.textContent = `${found.length} ${found.length === 1 ? "result" : "results"} for “${query}” · ${elapsedLabel} search time`;

    if (found.length) showResults(found);
    else showMessage("No results found", "Try a different term or a shorter query.");
  } catch (error) {
    if (error.name === "AbortError") return;
    meta.textContent = "Unable to complete search";
    showMessage("Search unavailable", error.message || "Please check the Flask server.");
  } finally {
    if (activeRequest === controller) {
      activeRequest = null;
      setLoading(false);
    }
  }
}

function reset() {
  if (activeRequest) activeRequest.abort();
  activeRequest = null;
  setLoading(false);
  app.classList.remove("has-results");
  input.value = "";
  list.replaceChildren();
  const pageUrl = new URL(window.location.href);
  pageUrl.searchParams.delete("q");
  window.history.replaceState(null, "", pageUrl);
  input.focus();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

form.addEventListener("submit", event => {
  event.preventDefault();
  run(input.value);
});

document.getElementById("chips").addEventListener("click", event => {
  if (event.target.classList.contains("chip")) run(event.target.textContent);
});

document.getElementById("newSearch").addEventListener("click", reset);

document.addEventListener("keydown", event => {
  const focusShortcut = (event.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) ||
    ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k");
  if (focusShortcut) { event.preventDefault(); input.focus(); }
  if (event.key === "Escape" && document.activeElement === input) input.blur();
});

themeToggle.addEventListener("click", () => {
  const next = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", next);
  themeToggle.setAttribute("aria-label", next === "light" ? "Switch to dark mode" : "Switch to light mode");
});

const initialQuery = new URL(window.location.href).searchParams.get("q");
if (initialQuery && initialQuery.trim()) run(initialQuery);
