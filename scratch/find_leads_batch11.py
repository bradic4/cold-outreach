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

candidate_domains_b11 = [
    # 1. Privatni domovi za stara lica (800€–1.500€/mes - visoka konverzija sa telefona)
    ("Dom za stara lica Milidom Lux", "https://milidomlux.rs/"),
    ("Dom za stara lica Senior Plus", "https://seniorplus.rs/"),
    ("Dom za stara lica Nana", "https://domnana.rs/"),
    ("Dom za stara lica Lug", "https://domlug.rs/"),
    ("Dom za stare Holiday House", "https://holidayhouse.rs/"),
    ("Dom za stara lica Avala Lux", "https://domzastareavalalux.rs/"),
    ("Dom za stara lica Zvezdara Lux", "https://zvezdaralux.rs/"),

    # 2. Mermer, granit, kvarc radne ploce & kamen (1.000€–10.000€)
    ("Mermer Granit Breza", "https://breza.rs/"),
    ("Kamenorezac Mermer Granit", "https://mermer-granit.rs/"),
    ("Kvarc Radne Ploce Beograd", "https://kvarcneploce.rs/"),
    ("Mermer Stil", "https://mermerstil.rs/"),
    ("Granit Kamen Inzenjering", "https://granit-kamen.rs/"),
    ("Stonex Mermer Granit", "https://stonex.rs/"),

    # 3. Distributeri medicinske i stomatoloske opreme (5.000€–50.000€)
    ("Medicom Sabac Oprema", "https://medicom.rs/"),
    ("Vicor Medicinska Oprema", "https://vicor.rs/"),
    ("Dental Medical Srbija", "https://dental-medical.rs/"),
    ("Superdent Stomatoloska Oprema", "https://superdent.rs/"),
    ("Medisal Oprema", "https://medisal.rs/"),
    ("Mikodental Tehnologija", "https://mikodental.rs/"),

    # 4. Industrijska automatizacija, PLC & elektromontaza
    ("Mikro Kontrol Automatizacija", "https://mikrokontrol.rs/"),
    ("Kolektor Inzenjering", "https://kolektor.rs/"),
    ("Uno-Lux Automatizacija", "https://unolux.rs/"),
    ("Automatika Beograd", "https://automatika.rs/"),
    ("Ibis Instrumenti", "https://ibis-instruments.com/"),

    # 5. Psihoterapija & Privatna savetovalista (diskretni mobilni buking)
    ("Psiholosko savetovalište Mozaik", "https://mozaikpsihoterapija.rs/"),
    ("Centar za psihoterapiju Korak", "https://korakpsihoterapija.rs/"),
    ("Psihoterapija Beograd", "https://psihoterapijabeograd.rs/"),
    ("Savetovaliste Entera", "https://entera.rs/")
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

found_leads_b11 = []
with ThreadPoolExecutor(max_workers=18) as executor:
    futures = [executor.submit(fetch_lead_deep, item) for item in candidate_domains_b11]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_b11.append(res)
            safe_name = res['name'].encode('ascii', 'replace').decode('ascii')
            print(f"FOUND: {safe_name} -> {res['email']}")
            sys.stdout.flush()

print(f"\nTotal leads found in batch 11: {len(found_leads_b11)}")
with open("scratch/fresh_leads_b11.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_b11, f, ensure_ascii=False, indent=2)
