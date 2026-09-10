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

candidate_domains_deep = [
    # 1. Stomatologija & Dentalni turizam
    ("Stomatologija Dr Bede Novi Sad", "https://drbede.com/"),
    ("Dr Veselinovic Stomatologija", "https://drveselinovic.rs/"),
    ("Ordinacija Dr Scepanovic", "https://drscepanovic.com/"),
    ("Dr Lopandic Stomatologija", "https://drlopandic.rs/"),
    ("Dental Magic Studio", "https://dentalmagic.rs/"),
    ("Dental Studio Vuckovic", "https://dentalvuckovic.rs/"),
    ("Dental Spa Nis", "https://dentalspa.co.rs/"),
    ("Stomatologija Dr Tomanovic", "https://drtomanovic.rs/"),
    ("Ordinacija Dentix", "https://dentix.rs/"),
    ("Dentalis Art Nis", "https://dentalisart.rs/"),
    ("Ordinacija Dr Milosevic", "https://stomatologijamilosevic.rs/"),
    ("Ordinacija Dr Radojkovic", "https://drradojkovic.rs/"),
    ("Ordinacija Dr Vranjes", "https://drvranjes.rs/"),
    ("Dentus Perfectus", "https://dentusperfectus.rs/"),
    ("Dr Ast Dental", "https://drast.rs/"),
    ("Dental Corner Beograd", "https://dentalcorner.rs/"),
    ("Ordinacija Lav Dental", "https://lavdental.rs/"),
    ("Modest Dental Centar", "https://modestdental.rs/"),
    ("Dental Centar Bobic", "https://dentalcentarbobic.rs/"),

    # 2. Arhitektura & Enterijeri
    ("Studio Linear Arhitektura", "https://linear.rs/"),
    ("Proaspekt Arhitektura", "https://proaspekt.com/"),
    ("Paripovic Arhitekti", "https://paripovic.rs/"),
    ("Studio Domino Dizajn", "https://dominostudio.rs/"),
    ("Studio Simovic", "https://studiosimovic.com/"),
    ("Takt Studio Arhitekti", "https://taktstudio.rs/"),
    ("Antipod Design Studio", "https://antipod.rs/"),
    ("INKa Studio Beograd", "https://inkastudio.rs/"),
    ("Spatial Design Studio", "https://spatialdesign.rs/"),
    ("Studio OBE Arhitektura", "https://studioobe.rs/"),
    ("Line 4 Design Arhitekti", "https://line4design.rs/"),
    ("DA Dizajn Arhitektura", "https://dadizajn.rs/"),
    ("Studio Metar Beograd", "https://studiometar.rs/"),
    ("Arhitektonski studio Modular", "https://modular.rs/"),
    ("Arhitektonski atelje Prostor", "https://ateljeprostor.rs/"),
    ("Biro Arhiform", "https://arhiform.rs/"),
    ("Studio 2B Arhitekti", "https://studio2b.rs/"),

    # 3. Toplotne pumpe, grejanje, solari
    ("Solaris Energy Srbija", "https://solaris-energy.rs/"),
    ("Helios Solar Sistemi", "https://helios-solar.rs/"),
    ("Telefon Inzenjering", "https://telefon-inzenjering.co.rs/"),
    ("Termo Servis Toplota", "https://termoservis.rs/"),
    ("Eko Toplotne Pumpe", "https://ekotoplotnepumpe.rs/"),
    ("Klima Eko Sistemi", "https://klimaeko.rs/"),
    ("Termokon Inzenjering", "https://termokon.rs/"),
    ("Solar Star Srbija", "https://solarstar.rs/"),
    ("Solar Monting", "https://solarmonting.rs/"),
    ("Klima BG Servis", "https://klimabg.rs/"),
    ("Termoprojekt Grejanje", "https://termoprojekt.com/"),
    ("Termo KGH", "https://termokgh.rs/"),
    ("Solar Tehnik", "https://solartehnik.rs/"),
    ("Toplotne Pumpe NS", "https://toplotnepumpens.rs/"),
    ("Frigo Sistem Rashlada", "https://frigosistem.rs/"),

    # 4. Privatne klinike & Medicina
    ("Poliklinika Sveti Jovan", "https://svetijovan.rs/"),
    ("Poliklinika Perinatal", "https://perinatal.rs/"),
    ("Poliklinika Pekic", "https://poliklinikapekic.com/"),
    ("Poliklinika Nada D", "https://poliklinikanadad.rs/"),
    ("Poliklinika Medicor", "https://medicor.rs/"),
    ("Klinika Genesis", "https://genesis.rs/"),
    ("Poliklinika Sunce", "https://poliklinikasunce.rs/"),
    ("Poliklinika Intermedic", "https://intermedic.rs/"),
    ("Poliklinika Kragujmedik", "https://kragujmedik.rs/"),
    ("Poliklinika Cardioprevent", "https://cardioprevent.rs/"),

    # 5. Bazeni & Opremanje
    ("Bibis Bazeni i Saune", "https://bibis.rs/"),
    ("Bazeni Srbija", "https://bazenisrbija.com/"),
    ("Marconio Wellness", "https://marconio.com/"),
    ("Aquaplan Bazeni", "https://aquaplan.rs/"),
    ("Pools and More", "https://bazeniioprema.rs/")
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def extract_valid_emails(html):
    raw_emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html))
    valid = []
    for e in raw_emails:
        ec = e.lower().strip()
        if not any(ec.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.css', '.js', '.avif')):
            if not any(x in ec for x in ['sentry', 'wix', 'example', 'domain', 'schema', 'test', 'bootstrap', 'wordpress', 'cloudflare', 'contact@yourdomain', 'email@', 'posao', 'job']):
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

found_leads_deep = []
with ThreadPoolExecutor(max_workers=15) as executor:
    futures = [executor.submit(fetch_lead_deep, item) for item in candidate_domains_deep]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_deep.append(res)
            safe_name = res['name'].encode('ascii', 'replace').decode('ascii')
            print(f"FOUND: {safe_name} -> {res['email']}")
            sys.stdout.flush()

print(f"\nTotal leads found deep: {len(found_leads_deep)}")
with open("scratch/fresh_leads_deep.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_deep, f, ensure_ascii=False, indent=2)
