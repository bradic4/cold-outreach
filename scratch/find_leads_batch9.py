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

candidate_domains_b9 = [
    # 1. Profesionalna ugostiteljska i pekarska oprema (2.000€–20.000€)
    ("Pekarska Oprema Tehnopek", "https://tehnopek.rs/"),
    ("Ugostiteljska Oprema Conto", "https://conto.rs/"),
    ("Gastro Oprema Srbija", "https://gastrooprema.rs/"),
    ("Profesionalna Oprema Termo", "https://termooprema.com/"),
    ("Pekarska Oprema Finans", "https://finans.rs/"),
    ("Bago Ugostiteljska Oprema", "https://bago.rs/"),
    ("Pekarska Mehanika", "https://pekarskamehanika.rs/"),

    # 2. Magnetna rezonanca, skener & radiologija (150€–400€ po pregledu)
    ("Dijagnosticki Centar Hram", "https://dchram.rs/"),
    ("MR Dijagnostika Beograd", "https://mrdijagnostika.rs/"),
    ("Magnetna Rezonanca Centar", "https://magnetnarezonanca.rs/"),
    ("Dijagnostika Medipol", "https://medipol.rs/"),
    ("Radiologija Centar", "https://radiologijacentar.rs/"),
    ("Poliklinika Antamedica MR", "https://antamedica.rs/"),

    # 3. Tehnicki pregled & Registracija vozila (kalkulator registracije)
    ("Tehnicki Pregled Sunce", "https://suncetehnicki.rs/"),
    ("Tehnicki Pregled Don", "https://tehnickipregleddon.rs/"),
    ("Tehnicki Pregled Signal", "https://tehnickipregledsignal.rs/"),
    ("Tehnicki Pregled Auto Servis", "https://tehnickipregled.rs/"),
    ("Agencija za registraciju vozila As", "https://registracija-vozila-as.rs/"),

    # 4. Poljoprivredna mehanizacija & Navodnjavanje (5.000€–50.000€)
    ("Agromarket Mehanizacija", "https://agromarket.rs/"),
    ("Agropanonka Traktori", "https://agropanonka.com/"),
    ("Kite DOO Mehanizacija", "https://kitedoo.rs/"),
    ("Skovran Poljomehanizacija", "https://skovran.rs/"),
    ("Sistem za navodnjavanje Skala", "https://skalagarden.com/"),
    ("Navodnjavanje Srbija", "https://navodnjavanje.rs/"),

    # 5. Laserski centri & Estetska medicina
    ("Laser Centar Trimedex", "https://trimedex.rs/"),
    ("Laser Derma Studio", "https://laserderma.rs/"),
    ("Epilion Poliklinika", "https://epilion.rs/"),
    ("Diva Clinic Centar", "https://divaclinic.rs/"),
    ("Estetik Studio Bel", "https://estetikstudiobel.rs/")
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

found_leads_b9 = []
with ThreadPoolExecutor(max_workers=18) as executor:
    futures = [executor.submit(fetch_lead_deep, item) for item in candidate_domains_b9]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_b9.append(res)
            safe_name = res['name'].encode('ascii', 'replace').decode('ascii')
            print(f"FOUND: {safe_name} -> {res['email']}")
            sys.stdout.flush()

print(f"\nTotal leads found in batch 9: {len(found_leads_b9)}")
with open("scratch/fresh_leads_b9.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_b9, f, ensure_ascii=False, indent=2)
