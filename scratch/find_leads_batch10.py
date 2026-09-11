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

candidate_domains_b10 = [
    # 1. Montazne kuce, kontejneri & brvnare (20.000€–80.000€ ugovori)
    ("Eko Kuca Montazne Kuce", "https://ekokuca.rs/"),
    ("Montazne Kuce Negal", "https://negal.rs/"),
    ("Montazne Kuce Maker", "https://maker.rs/"),
    ("Montazne Kuce Luks", "https://montazne-kuce.rs/"),
    ("Argus Inzenjering Kontejneri", "https://argus-eng.co.rs/"),
    ("Kontejneri Beograd", "https://kontejneribeograd.rs/"),
    ("Stambeni Kontejneri", "https://stambenikontejneri.com/"),
    ("Brvnare Srbija", "https://brvnare.rs/"),

    # 2. Ginekologija, 4D ultrazvuk & Prenatalna dijagnostika (500€–1.000€)
    ("Ginekoloska ordinacija Biljana Zivaljevic", "https://drzivaljevic.rs/"),
    ("Ginekoloska ordinacija Palmotic", "https://palmotic.rs/"),
    ("Ginekologija Demetra", "https://demetraordinacija.rs/"),
    ("Ginekoloska ordinacija Mladenovic", "https://drmladenovic.rs/"),
    ("Ginekologija Korak", "https://ordinacijakorak.rs/"),
    ("Ordinacija Dr Jeremic", "https://drjeremic.rs/"),
    ("Ginekologija Genesis Novi Sad", "https://genesis.rs/"),

    # 3. Ventilacija, klimatizacija & odimljavanje
    ("KGH Inzenjering", "https://kgh.rs/"),
    ("Ventilacija i Klima Sistem", "https://ventilacija.rs/"),
    ("Aeroteh Ventilacija", "https://aeroteh.rs/"),
    ("Air System Srbija", "https://airsystem.rs/"),
    ("Klima Vent Inzenjering", "https://klimavent.rs/"),

    # 4. Etno sela, vinarije & Vikend turizam (vikend aranzmani i odmori)
    ("Etno Selo Stanisici", "https://etno-selo.com/"),
    ("Etno Selo Babina Reka", "https://babinareka.rs/"),
    ("Etno Selo Vrdnicka Kula", "https://fruske-terme.com/"),
    ("Klub Reset Fruska Gora", "https://klubreset.rs/"),
    ("Platani Fruska Gora", "https://platani.rs/"),
    ("Kastel Ecka Zrenjanin", "https://kastelecka.com/"),

    # 5. Geomehanika, ispitivanje betona & konstrukcija
    ("Geomehanika Inzenjering", "https://geomehanika.rs/"),
    ("Laboratorija za Beton", "https://laboratorijazabeton.rs/"),
    ("Institut za Puteve", "https://institutzaputeve.rs/"),
    ("Projekt Inzenjering Beton", "https://projektinzenjering.rs/")
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

found_leads_b10 = []
with ThreadPoolExecutor(max_workers=18) as executor:
    futures = [executor.submit(fetch_lead_deep, item) for item in candidate_domains_b10]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_b10.append(res)
            safe_name = res['name'].encode('ascii', 'replace').decode('ascii')
            print(f"FOUND: {safe_name} -> {res['email']}")
            sys.stdout.flush()

print(f"\nTotal leads found in batch 10: {len(found_leads_b10)}")
with open("scratch/fresh_leads_b10.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_b10, f, ensure_ascii=False, indent=2)
