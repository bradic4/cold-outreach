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

candidates_more = [
    ("Poliklinika Cardioprevent Novi Sad", "https://cardioprevent.rs/"),
    ("Poliklinika Pekic Novi Sad", "https://poliklinikapekic.rs/"),
    ("Poliklinika Nada D Kragujevac", "https://poliklinikanadad.com/"),
    ("Klinika Perinatal Novi Sad", "https://poliklinikaperinatal.com/"),
    ("Poliklinika Medicor Nis", "https://medicor-nis.com/"),
    ("Dental Studio Vuckovic Nis", "https://vuckovicdental.rs/"),
    ("Ordinacija Dr Scepanovic Beograd", "https://dr-scepanovic.rs/"),
    ("Solar Star Sistemi", "https://solarstar.rs/"),
    ("Toplotne Pumpe Eko", "https://toplotne-pumpe.rs/"),
    ("Frigo Servis Beograd", "https://frigoservis.com/"),
    ("Termo KGH Inzenjering", "https://termokgh.co.rs/"),
    ("Studio OBE Arhitekti", "https://obe.rs/"),
    ("INKa Studio Arhitekti", "https://inka.rs/"),
    ("Spatial Design Enterijeri", "https://spatial.rs/"),
    ("Biro Arhiform Beograd", "https://arhiform.com/"),
    ("Aquaplan Bazeni Zrenjanin", "https://aquaplan.co.rs/"),
    ("Pools and More Bazeni", "https://bazeniioprema.com/"),
    ("Kuhinje Nolte Beograd", "https://noltekuhinje.rs/"),
    ("Enterijer Jankovic Novi Sad", "https://enterijerjankovic.com/"),
    ("Artinvest Centar", "https://artinvest.rs/")
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

found_leads_more = []
with ThreadPoolExecutor(max_workers=15) as executor:
    futures = [executor.submit(fetch_lead_deep, item) for item in candidates_more]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_more.append(res)
            safe_name = res['name'].encode('ascii', 'replace').decode('ascii')
            print(f"FOUND: {safe_name} -> {res['email']}")
            sys.stdout.flush()

print(f"\nTotal leads found more: {len(found_leads_more)}")
with open("scratch/fresh_leads_more.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_more, f, ensure_ascii=False, indent=2)
