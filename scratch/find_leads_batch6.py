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

candidate_domains_b6 = [
    # 1. Geodetske agencije & Katastar / Legalizacija (300€–2.000€ po poslu)
    ("Geodet Beograd", "https://geodet.rs/"),
    ("Geo Sistem Inzenjering", "https://geosistem.rs/"),
    ("Geoplan Beograd", "https://geoplan.rs/"),
    ("Geo Centar Kragujevac", "https://geocentar.rs/"),
    ("Geometar Beograd", "https://geometarbeograd.rs/"),
    ("Geodetski biro Tasa", "https://geodetskabiro.rs/"),
    ("Geo Max Kragujevac", "https://geomax.rs/"),

    # 2. Privatne predskolske ustanove & Vrtici (subvencije grada: 300€–500€/mes po detetu)
    ("Predskolska ustanova Trešnjober", "https://tresnjober.com/"),
    ("Privatni vrtic Povratak Prirodi", "https://povratakprirodi.rs/"),
    ("Privatna predskolska ustanova Play", "https://vrticplay.rs/"),
    ("Vrtic Happy Kids", "https://happykids.rs/"),
    ("Predskolska ustanova Mala Zvezda", "https://malazvezda.rs/"),
    ("Privatni vrtic Kreativno Pero", "https://kreativnopero.com/"),
    ("Privatna predskolska ustanova Zvoncaric", "https://zvoncaric.rs/"),

    # 3. Zastita na radu & BZR / PPZ (zakonska obaveza za sva pravna lica)
    ("Tehpro Zastita na radu", "https://tehpro.rs/"),
    ("Zastita Prevent Beograd", "https://zastitaprevent.rs/"),
    ("Centar za BZR", "https://centarzabzr.rs/"),
    ("BZR Inzenjering", "https://bzrinzenjering.rs/"),
    ("Zastita na radu Institut", "https://institut-znr.rs/"),
    ("Inspekt Zastita", "https://inspekt.rs/"),

    # 4. Industrijska rashlada, cileri & vitrine
    ("Frigo Bel", "https://frigobel.rs/"),
    ("Frigomont", "https://frigomont.rs/"),
    ("Hladnjace Srbija", "https://hladnjace.rs/"),
    ("Master Frigo", "https://masterfrigo.com/"),
    ("Frigo Zika", "https://frigozika.rs/"),
    ("Frigo San", "https://frigosan.rs/"),

    # 5. Spediteri, Carinjenje & Medjunarodni transport
    ("Milsped Spedicija", "https://milsped.com/"),
    ("Gebruder Weiss Srbija", "https://gw-world.com/"),
    ("Kuehne Nagel Srbija", "https://kuehne-nagel.com/"),
    ("Spedicija Tim Beograd", "https://spedicijatim.rs/"),
    ("Logistika Plus", "https://logistikaplus.rs/"),
    ("Alfa Sped Carina", "https://alfasped.rs/")
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def extract_valid_emails(html):
    raw_emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html))
    valid = []
    for e in raw_emails:
        ec = e.lower().strip()
        if not any(ec.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.css', '.js', '.avif')):
            if not any(x in ec for x in ['sentry', 'wix', 'example', 'domain', 'schema', 'test', 'bootstrap', 'wordpress', 'cloudflare', 'contact@yourdomain', 'email@', 'posao', 'job', 'privacy']):
                if ec not in history:
                    valid.append(ec)
    return valid

def fetch_lead_deep(item):
    name, base_url = item
    base_url = base_url.rstrip('/')
    urls_to_try = [base_url, f"{base_url}/kontakt", f"{base_url}/kontakt/", f"{base_url}/contact", f"{base_url}/contact/"]
    
    for u in urls_to_try:
        try:
            req = urllib.request.Request(u, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=3) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                emails = extract_valid_emails(html)
                if emails:
                    return {"name": name, "url": base_url, "email": emails[0]}
        except Exception:
            continue
    return None

found_leads_b6 = []
with ThreadPoolExecutor(max_workers=18) as executor:
    futures = [executor.submit(fetch_lead_deep, item) for item in candidate_domains_b6]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_b6.append(res)
            safe_name = res['name'].encode('ascii', 'replace').decode('ascii')
            print(f"FOUND: {safe_name} -> {res['email']}")
            sys.stdout.flush()

print(f"\nTotal leads found in batch 6: {len(found_leads_b6)}")
with open("scratch/fresh_leads_b6.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_b6, f, ensure_ascii=False, indent=2)
