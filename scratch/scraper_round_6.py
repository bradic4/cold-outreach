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

candidate_domains_6 = [
    ("Ordinacija Vukcevic", "https://vukcevicdental.com/"),
    ("Ordinacija Dr Popovic Dental", "https://drpopovic.com/"),
    ("Dental Studio Vuckovic", "https://dentalvuckovic.rs/"),
    ("Ordinacija Dental Art Beograd", "https://dentalart.rs/"),
    ("Modest Dental Centar", "https://modestdental.rs/"),
    ("Ordinacija Lav Dental", "https://lavdental.rs/"),
    ("Dentalis Art Nis", "https://dentalisart.rs/"),
    ("Dr Ast Dental Centar", "https://drast.rs/"),
    ("Studio MM Arhitekti", "https://studiomm.rs/"),
    ("Studio Linear Arhitektura", "https://linear.rs/"),
    ("Paripovic Arhitekti", "https://paripovic.rs/"),
    ("Studio Domino Enterijeri", "https://dominostudio.rs/"),
    ("Studio Simovic Arhitekti", "https://studiosimovic.com/"),
    ("Solaris Energy Srbija", "https://solaris-energy.rs/"),
    ("Telefon Inzenjering Solar", "https://telefon-inzenjering.co.rs/"),
    ("Termo Servis Toplota", "https://termoservis.rs/"),
    ("Eko Toplotne Pumpe", "https://ekotoplotnepumpe.rs/"),
    ("Klima Eko Sistemi", "https://klimaeko.rs/"),
    ("Poliklinika Sveti Jovan", "https://svetijovan.rs/"),
    ("Poliklinika Perinatal Novi Sad", "https://perinatal.rs/"),
    ("Poliklinika Pekic Novi Sad", "https://poliklinikapekic.com/"),
    ("Poliklinika Nada D Kragujevac", "https://poliklinikanadad.rs/")
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

found_leads_6 = []
with ThreadPoolExecutor(max_workers=15) as executor:
    futures = [executor.submit(fetch_email, item) for item in candidate_domains_6]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_6.append(res)
            print(f"FOUND: {res['name']} -> {res['email']}")
            sys.stdout.flush()

print(f"Total leads found in round 6: {len(found_leads_6)}")
with open("scratch/fresh_leads_6.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_6, f, ensure_ascii=False, indent=2)
