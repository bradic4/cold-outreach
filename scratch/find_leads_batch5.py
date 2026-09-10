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

candidate_domains_b5 = [
    # 1. Event centri & Ketering za firme/svadbe (1.000€–5.000€ po eventu)
    ("Event Centar Promenada", "https://promenada.rs/"),
    ("Event Centar Posh", "https://posh.rs/"),
    ("Ketering Bg", "https://keteringbg.rs/"),
    ("Stari Bunar Event Centar", "https://staribunar.rs/"),
    ("Klub Reset Novi Sad", "https://klubreset.com/"),
    ("Event Centar Kovilovo", "https://kovilovo.com/"),
    ("Sonce Ketering", "https://sonceketering.rs/"),
    ("Premijer Ketering", "https://premijerketering.rs/"),
    ("Restoran Topciderac", "https://topciderac.rs/"),
    ("Kalemegdanska Terasa", "https://kalemegdanskaterasa.com/"),

    # 2. Epoksidni podovi, hidroizolacija & industrijski podovi
    ("Epoksidni Podovi Srbija", "https://epoksidnipodovi.rs/"),
    ("Podovi Beograd", "https://podovibeograd.rs/"),
    ("Hidroizolacija Beograd", "https://hidroizolacijabeograd.rs/"),
    ("Epoxi Podovi", "https://epoxipodovi.rs/"),
    ("Sika Srbija", "https://srb.sika.com/"),
    ("Gradjevinska Hemija", "https://gradjevinskahemija.rs/"),
    ("Izolacija Tim", "https://izolacijatim.rs/"),

    # 3. Knjigovodstvene agencije za IT i B2B firme (Retainer 300€–1.000€/mes)
    ("Vizija Racunovodstvo", "https://vizija-racunovodstvo.rs/"),
    ("Knjigovodstvo Faktura", "https://faktura.rs/"),
    ("Knjigovodstvena agencija Profit", "https://profitbg.rs/"),
    ("Trivium Racunovodstvo", "https://trivium.rs/"),
    ("Eurofast Srbija", "https://eurofast.eu/"),
    ("Knjigovodstvo Bilans", "https://bilans.rs/"),
    ("Knjigovodstvena agencija Konsalting", "https://konsalting.rs/"),

    # 4. Specijalisticka medicina, laboratorije & dijagnostika
    ("Aqualab Laboratorije", "https://aqualab.rs/"),
    ("Jugolab Laboratorija", "https://jugolab.rs/"),
    ("Konzilijum Laboratorija", "https://konzilijum.rs/"),
    ("Poliklinika Cardioprevent NS", "https://cardioprevent.rs/"),
    ("Poliklinika Medicor Nis", "https://medicor.rs/"),
    ("Poliklinika Panacea", "https://panacea.rs/"),
    ("Poliklinika Kragujmedik", "https://kragujmedik.rs/"),
    ("Poliklinika Intermedic", "https://intermedic.rs/"),
    ("Poliklinika Pekic", "https://poliklinikapekic.com/"),

    # 5. Auto-skole & Vozacki ispiti (brzi mobilni upis)
    ("Auto skola Pravo", "https://autoskolapravo.rs/"),
    ("Auto skola Pavlin", "https://pavlin.rs/"),
    ("Auto skola Signal", "https://autoskolasignal.rs/"),
    ("Auto skola Fest", "https://autoskolafest.rs/"),
    ("Auto skola Gazela", "https://autoskolagazela.rs/"),
    ("Auto skola Desetka Auto", "https://desetkaauto.rs/")
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

found_leads_b5 = []
with ThreadPoolExecutor(max_workers=18) as executor:
    futures = [executor.submit(fetch_lead_deep, item) for item in candidate_domains_b5]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_b5.append(res)
            safe_name = res['name'].encode('ascii', 'replace').decode('ascii')
            print(f"FOUND: {safe_name} -> {res['email']}")
            sys.stdout.flush()

print(f"\nTotal leads found in batch 5: {len(found_leads_b5)}")
with open("scratch/fresh_leads_b5.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_b5, f, ensure_ascii=False, indent=2)
