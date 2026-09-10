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

candidate_domains_b4 = [
    # 1. Estetska i plasticna hirurgija (2.000€–5.000€ zahvati)
    ("Klinika Dr Colic", "https://dr-colic.com/"),
    ("Klinika Diona", "https://diona.rs/"),
    ("Klinika Varis", "https://klinikavaris.com/"),
    ("Ordinacija dr Stojicevic", "https://stojicevic.rs/"),
    ("Clinic Olymp Novi Sad", "https://clinicolymp.com/"),
    ("Klinika Rea Medika", "https://reamedika.rs/"),
    ("Poliklinika Gracia Medika", "https://graciamedika.com/"),
    ("Poliklinika Medicor Nis", "https://medicor.rs/"),
    ("Poliklinika Perinatal", "https://perinatal.rs/"),
    ("Poliklinika Cardioprevent", "https://cardioprevent.rs/"),
    ("Poliklinika Nada D Kragujevac", "https://poliklinikanadad.rs/"),
    ("Poliklinika Kragujmedik", "https://kragujmedik.rs/"),
    ("Bolnica Ferona Novi Sad", "https://ferona.rs/"),

    # 2. Arhitektura, inzenjering & urbanizam
    ("Proaspekt Arhitektura", "https://proaspekt.com/"),
    ("Paripovic Arhitekti", "https://paripovic.rs/"),
    ("Studio Simovic Arhitekti", "https://studiosimovic.com/"),
    ("Takt Studio", "https://taktstudio.rs/"),
    ("DA Dizajn Arhitektura", "https://dadizajn.rs/"),
    ("Studio Metar Beograd", "https://studiometar.rs/"),
    ("Arhitektonski studio Linear", "https://linear.rs/"),
    ("Spatial Design Studio", "https://spatialdesign.rs/"),
    ("Studio 2B Arhitekti", "https://studio2b.rs/"),
    ("Atelje Prostor", "https://ateljeprostor.rs/"),
    ("Biro Arhiform", "https://arhiform.rs/"),
    ("Kuzmanov and Partners", "https://kuzmanovandpartners.com/"),

    # 3. Solari, toplotne pumpe & grejanje
    ("Solaris Energy Srbija", "https://solaris-energy.rs/"),
    ("Helios Solar Sistemi", "https://helios-solar.rs/"),
    ("Termo Servis Toplota", "https://termoservis.rs/"),
    ("Eko Toplotne Pumpe", "https://ekotoplotnepumpe.rs/"),
    ("Klima Eko Sistemi", "https://klimaeko.rs/"),
    ("Termokon Inzenjering", "https://termokon.rs/"),
    ("Solar Star Srbija", "https://solarstar.rs/"),
    ("Solar Monting", "https://solarmonting.rs/"),
    ("Klima BG Servis", "https://klimabg.rs/"),
    ("Termo KGH", "https://termokgh.rs/"),
    ("Solar Tehnik", "https://solartehnik.rs/"),
    ("Toplotne Pumpe NS", "https://toplotnepumpens.rs/"),
    ("Frigo Sistem", "https://frigosistem.rs/"),

    # 4. ALU & PVC stolarija, staklene fasade & ograde (poslovi 3.000€–30.000€)
    ("Sunce Marinkovic Kragujevac", "https://suncemarinkovic.com/"),
    ("Aluroll Batocina", "https://aluroll.rs/"),
    ("Roplasto PVC", "https://roplasto.rs/"),
    ("Betaplast Novi Sad", "https://betaplast.rs/"),
    ("Stolarija Petkovic", "https://stolarijapetkovic.rs/"),
    ("Inoutic PVC", "https://inoutic.rs/"),
    ("Megaplast PVC", "https://megaplast.rs/"),
    ("Hram 032 Stolarija", "https://hram032.rs/"),

    # 5. Veterinarske klinike & bolnice (urgencije 24/7)
    ("Veterinarska bolnica Beograd", "https://vetklinikabeograd.rs/"),
    ("Veterinarska ambulanta Spina", "https://spina.rs/"),
    ("Vet Centar Beograd", "https://vetcentar.rs/"),
    ("Veterinarska klinika Novak", "https://vetnovak.com/"),
    ("Pet Vet Klinika", "https://petvet.rs/")
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

found_leads_b4 = []
with ThreadPoolExecutor(max_workers=18) as executor:
    futures = [executor.submit(fetch_lead_deep, item) for item in candidate_domains_b4]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_b4.append(res)
            safe_name = res['name'].encode('ascii', 'replace').decode('ascii')
            print(f"FOUND: {safe_name} -> {res['email']}")
            sys.stdout.flush()

print(f"\nTotal leads found in batch 4: {len(found_leads_b4)}")
with open("scratch/fresh_leads_b4.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_b4, f, ensure_ascii=False, indent=2)
