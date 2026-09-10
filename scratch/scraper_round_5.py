import urllib.request
import re
import json
import ssl
import sys
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')
socket.setdefaulttimeout(3)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with open('.mp/sent_emails_history.txt', 'r', encoding='utf-8', errors='ignore') as f:
    history = set(line.strip().lower() for line in f if line.strip())

candidate_domains_5 = [
    # Wineries / HoReCa
    ("Vinarija Deuric", "https://deuricvinarija.rs/"),
    ("Vinarija Radovanovic", "https://vinarijaradovanovic.rs/"),
    ("Vinarija Temet", "https://temet.rs/"),
    ("Vinarija Matalj", "https://mataljvinarija.rs/"),
    ("Vinarija Cilic", "https://cilic.rs/"),
    ("Vinarija Bikicki", "https://bikicki.rs/"),
    ("Vinarija Erdevik", "https://vinarijaerdevik.com/"),
    ("Vinarija Virtus", "https://vinarijavirtus.rs/"),
    
    # E-commerce & Fashion / Cosmetics
    ("Ivko Woman", "https://ivko.com/"),
    ("Mona Fashion", "https://mona.rs/"),
    ("Tiffany Production", "https://tiffanyproduction.com/"),
    ("Legend World Wide", "https://legend.rs/"),
    ("Extreme Intimo", "https://extremeintimo.com/"),
    ("Hedera Vita", "https://hederavita.rs/"),
    ("Koozmetik Natural", "https://koozmetik.rs/"),
    ("All Nut Kozmetika", "https://allnut.rs/"),

    # Removal / Logistics / Storage
    ("A1 Selidbe Beograd", "https://a1selidbe.rs/"),
    ("Pro Selidbe", "https://proselidbe.rs/"),
    ("Beo Selidbe", "https://beoselidbe.rs/"),
    ("Selidbe BG", "https://selidbebg.rs/"),
    ("Alisa Selidbe", "https://alisaselidbe.rs/"),
    ("Spremni za Selidbu", "https://selidbei得prevoz.rs/")
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def fetch_email(item):
    name, url = item
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=3) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            raw_emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html))
            valid = []
            for e in raw_emails:
                ec = e.lower().strip()
                if not any(ec.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.css', '.js', '.avif')):
                    if not any(x in ec for x in ['sentry', 'wix', 'example', 'domain', 'schema', 'test', 'bootstrap', 'wordpress', 'cloudflare', 'contact@yourdomain', 'email@']):
                        if ec not in history:
                            valid.append(ec)
            if valid:
                return {"name": name, "url": url, "email": valid[0]}
    except Exception:
        pass
    return None

found_leads_5 = []
with ThreadPoolExecutor(max_workers=15) as executor:
    futures = [executor.submit(fetch_email, item) for item in candidate_domains_5]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_5.append(res)
            print(f"FOUND: {res['name']} -> {res['email']}")
            sys.stdout.flush()

print(f"Total leads found in round 5: {len(found_leads_5)}")
with open("scratch/fresh_leads_5.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_5, f, ensure_ascii=False, indent=2)
