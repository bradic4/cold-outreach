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

candidate_domains_4 = [
    # Dental clinics
    ("Dental Studio Vuckovic", "https://dentalvuckovic.rs/"),
    ("Ordinacija Dr Scepanovic", "https://drscepanovic.com/"),
    ("Dr Simic Dental", "https://drsimic.rs/"),
    ("Dental Centar Savic", "https://savicdental.rs/"),
    ("Ordinacija Dentalux Nis", "https://dentaluxnis.rs/"),
    ("Stomatologija Dr Tomanovic", "https://drtomanovic.rs/"),
    ("Ordinacija Dentix", "https://dentix.rs/"),
    ("Dental Spa Centar Nis", "https://dentalspa.co.rs/"),
    ("Ordinacija Dr Radojkovic", "https://drradojkovic.rs/"),
    ("Stomatoloska ordinacija Vident", "https://vident.rs/"),
    ("Ordinacija Medent", "https://medent.rs/"),
    ("Dental Office Beograd", "https://dentaloffice.rs/"),
    ("Ordinacija Dentalis Beograd", "https://dentalis.rs/"),
    ("Dental Estetik Centar", "https://dentalestetikcentar.com/"),
    ("Dental Centar Kragujevac", "https://dentalcentarkg.rs/"),

    # Architects & Interior Design
    ("Studio Archviz", "https://archviz.rs/"),
    ("Biro Cube", "https://bureaucube.com/"),
    ("Studio 3D Projekt", "https://3dprojekt.rs/"),
    ("Arhitektonski studio Modular", "https://modular.rs/"),
    ("Studio Forma", "https://forma.rs/"),
    ("Arhitektonski atelje Prostor", "https://ateljeprostor.rs/"),
    ("Studio Struktura", "https://struktura.rs/"),
    ("Studio DA Dizajn", "https://dadizajn.rs/"),
    ("Biro Arhiform", "https://arhiform.rs/"),
    ("Enterijer Jankovic", "https://enterijer-jankovic.co.rs/"),
    ("Studio Prodom", "https://prodom.rs/"),
    ("Arhitektonski biro Gradnja", "https://birogradnja.rs/"),
    ("Architehna Studio", "https://architehna.rs/"),
    ("Studio 2B Arhitekti", "https://studio2b.rs/"),
    ("Studio Linija", "https://studiolinija.rs/"),

    # Solar & HVAC & Insulation
    ("Klima Pingvin", "https://klimapingvin.rs/"),
    ("Solaris Energy", "https://solaris-energy.rs/"),
    ("Frigo Servis", "https://frigoservis.rs/"),
    ("Termo KGH", "https://termokgh.rs/"),
    ("Solar Monting", "https://solarmonting.rs/"),
    ("Eko Solar Group", "https://ekosolargroup.rs/"),
    ("Klima Centar", "https://klimacentar.rs/"),
    ("Termo Oprema", "https://termooprema.rs/"),
    ("Klima Eko", "https://klimaeko.rs/"),
    ("Solar Tehnik", "https://solartehnik.rs/"),
    ("Toplotne Pumpe NS", "https://toplotnepumpens.rs/"),
    ("Frigo Sistem", "https://frigosistem.rs/"),
    ("Grejanje i Solari", "https://grejanje-solari.rs/"),
    ("Klima Teh", "https://klimateh.rs/"),

    # Medical clinics & Diagnostics & Surgery
    ("Poliklinika Human Nis", "https://poliklinikahuman.rs/"),
    ("Poliklinika Medicor", "https://medicor.rs/"),
    ("Klinika Genesis Novi Sad", "https://genesis.rs/"),
    ("Poliklinika Panacea", "https://panacea.rs/"),
    ("Poliklinika Euromedik", "https://euromedik.rs/"),
    ("Poliklinika Roncevic", "https://poliklinikaroncevic.com/"),
    ("Poliklinika Gracia", "https://graciamedika.com/"),
    ("Klinika Svjetlost", "https://svjetlost.rs/"),
    ("Poliklinika Sunce", "https://poliklinikasunce.rs/"),
    ("Bolnica Sveti Jovan", "https://svetijovan.rs/"),
    ("Poliklinika Nada D", "https://poliklinikanadad.rs/"),
    ("Poliklinika Pekic", "https://poliklinikapekic.com/"),
    ("Poliklinika Intermedic", "https://intermedic.rs/")
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

found_leads_4 = []
with ThreadPoolExecutor(max_workers=15) as executor:
    futures = [executor.submit(fetch_email, item) for item in candidate_domains_4]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_4.append(res)
            print(f"FOUND: {res['name']} -> {res['email']}")
            sys.stdout.flush()

print(f"Total leads found in round 4: {len(found_leads_4)}")
with open("scratch/fresh_leads_4.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_4, f, ensure_ascii=False, indent=2)
