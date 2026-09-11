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

candidate_domains_b7 = [
    # 1. HR agencije & Regrutacija radnika (kao Novotek HOT lead!)
    ("ManpowerGroup Srbija", "https://manpowergroup.rs/"),
    ("Adecco Srbija", "https://adecco.rs/"),
    ("Gi Group Srbija", "https://gigroup.rs/"),
    ("Dekra zaposljavanje", "https://dekra-zaposljavanje.rs/"),
    ("Kozomara HR", "https://kozomara.rs/"),
    ("HES regrutacija", "https://hes.rs/"),
    ("Hill International Srbija", "https://hill-international.com/"),
    ("Trenkwalder Srbija", "https://trenkwalder.rs/"),

    # 2. Kancelarijski namestaj & Akusticne pregrade / Fit-out
    ("Nitea Kancelarijski Namestaj", "https://nitea.rs/"),
    ("Kiteh Namestaj", "https://kiteh.rs/"),
    ("Kolex Namestaj", "https://kolex.rs/"),
    ("Antares Stolice", "https://antares-stolice.com/"),
    ("Ergon Kancelarijski Namestaj", "https://ergon.rs/"),
    ("Modrulj Stolice i Namestaj", "https://kancelarijske-stolice.com/"),
    ("Office Pro Namestaj", "https://officepro.rs/"),

    # 3. Automatska vrata, kapije, rampe & motori
    ("Nice Automatik Beograd", "https://nice.rs/"),
    ("Roloplast Mosic", "https://roloplastmosic.rs/"),
    ("Automatska Vrata Somfy", "https://somfy.rs/"),
    ("Bramont Kapije", "https://bramont.rs/"),
    ("Protector Vrata", "https://protector.rs/"),
    ("Segmentna Vrata Roll", "https://roll.rs/"),

    # 4. Dermatologija & Laserski centri (Anti-aging, laserska hirurgija)
    ("Diva Medical", "https://divamedical.rs/"),
    ("Dermatoloska ordinacija Dr Babovic", "https://drbabovic.com/"),
    ("Epilion Dermis", "https://epilion.rs/"),
    ("Laser Centar Trimedex", "https://trimedex.rs/"),
    ("Ordinacija Derma Viva", "https://dermaviva.rs/"),
    ("Laser Derma Beograd", "https://laserderma.rs/"),
    ("Dermatoloska ordinacija Vukovic", "https://dermavukovic.rs/"),

    # 5. VIP transferi & Kombi prevoz
    ("Gea Tours Transferi", "https://geatours.rs/"),
    ("Terra Travel Kombi Prevoz", "https://terratravel.rs/"),
    ("Limo Service Beograd", "https://limoservicebeograd.rs/"),
    ("Belgrade Airport Transfer", "https://belgradeairporttransfer.com/"),
    ("Prevoz Putnika Srbija", "https://prevozputnika.rs/")
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

found_leads_b7 = []
with ThreadPoolExecutor(max_workers=18) as executor:
    futures = [executor.submit(fetch_lead_deep, item) for item in candidate_domains_b7]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_b7.append(res)
            safe_name = res['name'].encode('ascii', 'replace').decode('ascii')
            print(f"FOUND: {safe_name} -> {res['email']}")
            sys.stdout.flush()

print(f"\nTotal leads found in batch 7: {len(found_leads_b7)}")
with open("scratch/fresh_leads_b7.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_b7, f, ensure_ascii=False, indent=2)
