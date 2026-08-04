from duckduckgo_search import DDGS

with DDGS() as ddgs:
    results = list(ddgs.text("stomatoloska ordinacija Beograd", max_results=20))
    print("DDGS results:", len(results))
    for r in results:
        print(" -", r.get("title"), "-->", r.get("href"))
