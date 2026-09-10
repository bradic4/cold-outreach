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

candidate_domains_ext = [
    # Ginekologija, VTO & Poliklinike
    ("Klinika Genesis Novi Sad", "https://genesis.rs/"),
    ("Specijalna bolnica Ferona", "https://ferona.rs/"),
    ("Poliklinika Gracia Medika Beograd", "https://graciamedika.rs/"),
    ("Poliklinika Medicor Nis", "https://poliklinikamedicor.rs/"),
    ("Specijalisticka ordinacija Dermavita", "https://dermavita.rs/"),
    ("Poliklinika Cardioprevent Novi Sad", "https://poliklinikacardioprevent.rs/"),
    ("Poliklinika Kragujmedik", "https://kragujmedik.com/"),
    ("Poliklinika Sunce Kragujevac", "https://poliklinikasunce.com/"),

    # Arhitektura & Inzenjering
    ("Studio Linear Beograd", "https://linear-studio.rs/"),
    ("Studio Architehna", "https://architehna.rs/"),
    ("Biro Cube Partners", "https://bureaucube.com/"),
    ("Arhitektonski studio Modular", "https://modular.rs/"),
    ("Proaspekt Biro", "https://proaspekt.rs/"),
    ("Studio 2B Arhitektura", "https://2b.rs/"),
    ("Atelje Prostor Arhitektura", "https://prostor.rs/"),

    # Toplotne pumpe, grejanje, solari
    ("Solaris Energy", "https://solarisenergy.rs/"),
    ("Helios Solar Beograd", "https://helios-solar.com/"),
    ("Klima M Inzenjering", "https://klimam.com/"),
    ("Termo Servis Toplota", "https://termoservis.com/"),
    ("Frigo Oprema Beograd", "https://frigo-oprema.rs/"),
    ("Klima Eko Sistemi", "https://klima-eko.rs/"),

    # Opremanje & Namestaj po meri (karte 2.000€–10.000€)
    ("Enterijer Jankovic", "https://enterijer-jankovic.rs/"),
    ("Dallas Namestaj Tutin", "https://dallas.rs/"),
    ("Forma Ideale B2B", "https://formaideale.rs/"),
    ("Simpo Opremanje Hotela", "https://simpo.rs/"),
    ("Atlas Namestaj Uzice", "https://atlasnamestaj.rs/")
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

found_leads_ext = []
with ThreadPoolExecutor(max_workers=18) as executor:
    futures = [executor.submit(fetch_lead_deep, item) for item in candidate_domains_ext]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_ext.append(res)
            safe_name = res['name'].encode('ascii', 'replace').decode('ascii')
            print(f"FOUND EXT: {safe_name} -> {res['email']}")
            sys.stdout.flush()

print(f"\nTotal leads found ext: {len(found_leads_ext)}")
with open("scratch/fresh_leads_ext.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_ext, f, ensure_ascii=False, indent=2)
