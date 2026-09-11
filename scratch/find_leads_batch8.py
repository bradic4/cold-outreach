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

candidate_domains_b8 = [
    # 1. Kuhinje po meri & Ugradni plakari (1.500€–5.000€ po stanu)
    ("Stolarija Zikic", "https://stolarijazikic.rs/"),
    ("Enterijeri Petrovic", "https://enterijeripetrovic.rs/"),
    ("Dipo Kuhinje", "https://dipo.rs/"),
    ("Kuhinje po meri Art", "https://kuhinjepomeri.rs/"),
    ("Studio Stil Namestaj", "https://studiostil.rs/"),
    ("M Enterijer Kuhinje", "https://menterijer.rs/"),
    ("Namestaj Danica", "https://danica.rs/"),
    ("Lignum Kuhinje", "https://lignum.rs/"),

    # 2. Kotlovi na pelet, grejanje & toplotne pumpe (Pik jesenje potraznje)
    ("Alfa Plam Vranje", "https://alfaplam.rs/"),
    ("MBS Milan Blagojevic Smederevo", "https://mbs.rs/"),
    ("Kepet Kotlovi", "https://kepo.rs/"),
    ("Termomont Simanovci", "https://termomont.rs/"),
    ("Radijator Inzenjering Kraljevo", "https://radijator.rs/"),
    ("Topling Kotlovi", "https://topling.rs/"),
    ("Eko Step Pellet", "https://ekosteppellet.rs/"),

    # 3. Fizikalna terapija, ortopedija & sportska medicina
    ("Fizio Centar Beograd", "https://fiziocentar.rs/"),
    ("Fizikalna terapija Fizio Tim", "https://fiziotim.rs/"),
    ("Master Fizikal", "https://masterfizikal.rs/"),
    ("Fizioterapija Beograd", "https://fizioterapijabeograd.rs/"),
    ("Ambulanta Fizio Balance", "https://fiziobalance.rs/"),
    ("Ortopedija Beograd", "https://ortopedijabeograd.rs/"),
    ("Ambulanta Vita Maxima", "https://vitamaxima.rs/"),

    # 4. Advokati za privredu, IT i nekretnine (B2B satnice i ugovori)
    ("Advokatska kancelarija Vukovic i Partneri", "https://vp.rs/"),
    ("Advokatska kancelarija Zivkovic Samardzic", "https://zslaw.rs/"),
    ("Advokatska kancelarija Gecic Law", "https://geciclaw.com/"),
    ("Advokatska kancelarija Stankovic i Partneri", "https://stankovicandpartners.com/"),
    ("Advokatska kancelarija Petosevic", "https://petosevic.com/"),

    # 5. Specijalizovani servisi za automatske menjace i premijum vozila
    ("Servis Automatskih Menjaca Slavko", "https://servisautomatskihmenjaca.com/"),
    ("Auto Centar Petrovic", "https://autocentarpetrovic.rs/"),
    ("BMW Servis Radulovic", "https://radulovic-group.com/"),
    ("Mercedes Servis Mikom", "https://mikom.mercedes-benz.rs/"),
    ("Audi Servis Porsche Ada", "https://porscheada.rs/")
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

found_leads_b8 = []
with ThreadPoolExecutor(max_workers=18) as executor:
    futures = [executor.submit(fetch_lead_deep, item) for item in candidate_domains_b8]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_b8.append(res)
            safe_name = res['name'].encode('ascii', 'replace').decode('ascii')
            print(f"FOUND: {safe_name} -> {res['email']}")
            sys.stdout.flush()

print(f"\nTotal leads found in batch 8: {len(found_leads_b8)}")
with open("scratch/fresh_leads_b8.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_b8, f, ensure_ascii=False, indent=2)
