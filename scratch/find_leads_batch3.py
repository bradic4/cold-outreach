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

candidate_domains_b3 = [
    # 1. Stomatologija & Dental Tourism
    ("Dr Veselinovic Stomatologija", "https://drveselinovic.rs/"),
    ("Ordinacija Dr Scepanovic", "https://drscepanovic.com/"),
    ("Dr Lopandic Stomatologija", "https://drlopandic.rs/"),
    ("Dental Magic Studio", "https://dentalmagic.rs/"),
    ("Implant Centar Beograd", "https://implantcentar.rs/"),
    ("Dental Studio Vuckovic", "https://dentalvuckovic.rs/"),
    ("Dental Corner Esthetics", "https://dentalcorner.rs/"),
    ("Dental Spa Nis", "https://dentalspa.co.rs/"),
    ("Stomatologija Dr Tomanovic", "https://drtomanovic.rs/"),
    ("Ordinacija Dentix", "https://dentix.rs/"),
    ("Dentalis Art Nis", "https://dentalisart.rs/"),
    ("Dental Estetik Centar", "https://dentalestetikcentar.com/"),
    ("Ordinacija Dr Milosevic", "https://stomatologijamilosevic.rs/"),
    ("Ordinacija Dr Radojkovic", "https://drradojkovic.rs/"),
    ("Ordinacija Dr Vranjes", "https://drvranjes.rs/"),
    ("Dentus Perfectus", "https://dentusperfectus.rs/"),

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
    ("Studio Archviz 3D", "https://archviz.rs/"),
    ("Arhitektonski studio Modular", "https://modular.rs/"),
    ("Arhitektonski atelje Prostor", "https://ateljeprostor.rs/"),
    ("Biro Arhiform", "https://arhiform.rs/"),
    ("Studio 2B Arhitekti", "https://studio2b.rs/"),

    # 3. Toplotne pumpe, grejanje, solari, klimatizacija
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

    # 4. Privatne klinike & Medicina / Estetika
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

    # 5. Bazeni, Saune & Wellnes / Luksuzno opremanje
    ("Bibis Bazeni i Saune", "https://bibis.rs/"),
    ("Bazeni Srbija", "https://bazenisrbija.com/"),
    ("Marconio Wellness", "https://marconio.com/"),
    ("Aquaplan Bazeni", "https://aquaplan.rs/"),
    ("Pools and More", "https://bazeniioprema.rs/")
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
                    if not any(x in ec for x in ['sentry', 'wix', 'example', 'domain', 'schema', 'test', 'bootstrap', 'wordpress', 'cloudflare', 'contact@yourdomain', 'email@', 'posao', 'job']):
                        if ec not in history:
                            valid.append(ec)
            if valid:
                return {"name": name, "url": url, "email": valid[0]}
    except Exception:
        pass
    return None

found_leads_b3 = []
with ThreadPoolExecutor(max_workers=15) as executor:
    futures = [executor.submit(fetch_email, item) for item in candidate_domains_b3]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_b3.append(res)
            safe_name = res['name'].encode('ascii', 'replace').decode('ascii')
            print(f"FOUND: {safe_name} -> {res['email']}")
            sys.stdout.flush()

print(f"\nTotal leads found in batch 3: {len(found_leads_b3)}")
with open("scratch/fresh_leads_b3.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_b3, f, ensure_ascii=False, indent=2)
