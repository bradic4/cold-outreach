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

candidate_domains_broad = [
    # Eye Clinics (Oftalmologija - huge ticket 1.000 - 3.000 EUR)
    ("Klinika Maja Nis", "https://klinikamaja.rs/"),
    ("Ocna kuca Profesional", "https://profesionaldrkovacevic.com/"),
    ("Specijalna bolnica za oftamologiju Milos Klinika", "https://milosklinika.medigroup.rs/"),
    ("Ocni Centar Dzunic", "https://ocnicentardzunic.rs/"),
    ("Ocna Klinika Vidar", "https://vidar.rs/"),
    ("Klinika LaserFocus", "https://laserfocus.eu/"),
    ("Perfect Vision Subotica", "https://kucazdravlja.rs/"),

    # Dental clinics across Serbia
    ("Ordinacija Dr Tomanovic", "https://drtomanovic.com/"),
    ("Dental Spa Centar", "https://dentalspacentar.com/"),
    ("Stomatologija Lopandic", "https://drlopandic.com/"),
    ("Dental Art Studio", "https://dentalartstudio.rs/"),
    ("Ordinacija Dentart", "https://dentart.rs/"),
    ("Ordinacija Dr Zoric", "https://drzoric.rs/"),
    ("Dental Estetik Centar BG", "https://dentalestetikcentar.rs/"),
    ("Klinika Varis", "https://klinikavaris.com/"),
    ("Stomatologija Magic", "https://dentalmagicstudio.com/"),
    ("Dental Centar Kragujevac", "https://dentalcentar.rs/"),

    # Architects & High-ticket Interior / Fit-out
    ("Studio OBE", "https://studio-obe.com/"),
    ("Studio Architehna", "https://architehna.com/"),
    ("Arhitektonski studio Modular", "https://modular.co.rs/"),
    ("Studio Forma Arhitektura", "https://forma-arhitektura.rs/"),
    ("Studio Metar", "https://metarstudio.rs/"),
    ("DA Dizajn Biro", "https://da-dizajn.rs/"),
    ("Atelje Prostor", "https://ateljeprostor.com/"),
    ("Studio Prodom NS", "https://prodom.co.rs/"),
    ("Arhitektonski biro Linear", "https://linear.co.rs/"),
    ("Studio Domino Enterijeri", "https://dominostudio.com/"),

    # Solar, Heating, HVAC
    ("Solar Star Srbija", "https://solarstar.co.rs/"),
    ("Helios Solar", "https://heliossolar.rs/"),
    ("Solaris Energy Srbija", "https://solaris-energy.com/"),
    ("Klima Eko", "https://klimaeko.com/"),
    ("Termo KGH Grejanje", "https://termokgh.com/"),
    ("Termoprojekt Beograd", "https://termoprojekt.rs/"),
    ("Toplotne Pumpe NS", "https://toplotnepumpe-ns.rs/"),
    ("Solar Tehnik Sistemi", "https://solartehnik.com/"),

    # Luxury furniture po meri & Kuhinje (1.500 - 5.000 EUR)
    ("Artinvest Namestaj", "https://artinvest.co.rs/"),
    ("Enterijer Jankovic", "https://enterijer-jankovic.com/"),
    ("Dallas Namestaj", "https://dallasnamestaj.com/"),
    ("Linea Milanovic", "https://lineamilanovic.rs/"),
    ("Nolte Kuhinje Srbija", "https://kuhinjenolte.rs/"),
    ("Eurosalon", "https://eurosalon.com/")
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

found_leads_broad = []
with ThreadPoolExecutor(max_workers=15) as executor:
    futures = [executor.submit(fetch_lead_deep, item) for item in candidate_domains_broad]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_broad.append(res)
            safe_name = res['name'].encode('ascii', 'replace').decode('ascii')
            print(f"FOUND: {safe_name} -> {res['email']}")
            sys.stdout.flush()

print(f"\nTotal leads found broad: {len(found_leads_broad)}")
with open("scratch/fresh_leads_broad.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_broad, f, ensure_ascii=False, indent=2)
