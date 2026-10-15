import urllib.request
import urllib.parse
import re
import json

def ddg_search(query):
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            links = re.findall(r'<a class="result__url" href="([^"]+)"', html)
            clean = []
            for l in links:
                if "uddg=" in l:
                    actual = urllib.parse.unquote(l.split("uddg=")[1].split("&")[0])
                    clean.append(actual)
                elif l.startswith("http"):
                    clean.append(l)
            return clean
    except Exception as e:
        print(f"DDG query failed for {query}: {e}")
        return []

queries = [
    '"bespoke kitchens" "joinery" "Surrey" "@" site:.co.uk',
    '"bespoke kitchens" "cabinetry" "Cheshire" "@" site:.co.uk',
    '"bespoke joinery" "fitted kitchens" "Oxfordshire" "@" site:.co.uk',
    '"handcrafted kitchens" "bespoke" "Hampshire" "@" site:.co.uk',
    '"bespoke kitchens" "Belfast" "@" site:.co.uk',
    '"architectural joinery" "bespoke kitchens" "Kent" "@" site:.co.uk',
    '"bespoke kitchens" "Belfast" "@" site:.co.uk',
    '"bespoke furniture" "kitchens" "Antrim" "@" site:.co.uk',
    '"custom kitchens" "joinery" "Yorkshire" "@" site:.co.uk'
]

urls = set()
for q in queries:
    res = ddg_search(q)
    print(f"Query '{q[:40]}...' found {len(res)} results")
    for r in res:
        # filter out directories and major aggregators
        skip = ["houzz", "yell", "checkatrade", "bark", "facebook", "instagram", "linkedin", "gumtree", "wikipedia", "pinterest", "trustatrader", "mybuilder", "ratedpeople"]
        if not any(s in r.lower() for s in skip):
            # simplify to base domain
            m = re.match(r'(https?://[^/]+)', r)
            if m:
                urls.add(m.group(1))

print(f"\nTotal candidate base URLs found: {len(urls)}")
with open(".mp/outlook_search_candidates.json", "w", encoding="utf-8") as f:
    json.dump(list(urls), f, indent=2)
print("Saved to .mp/outlook_search_candidates.json")
