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

candidate_domains = [
    # Dental / Dental Tourism
    ("Ordinacija Dentalux", "https://dentalux.rs/"),
    ("Lopicic Dental", "https://lopicic.com/"),
    ("Maglajlic Dental", "https://ordinacijamaglajlic.rs/"),
    ("Dental Plaza", "https://dentalplaza.rs/"),
    ("Dr Dragas Dental", "https://drdragas.rs/"),
    ("Eurodentist", "https://eurodentist.rs/"),
    ("Dental Studio Magic", "https://dentalmagic.rs/"),
    ("Implant Studio", "https://implantstudio.rs/"),
    ("Crown Dental", "https://crowndental.rs/"),
    ("Ordinacija Pavlovic", "https://stomatologijapavlovic.rs/"),
    ("Modest Dental", "https://modestdental.rs/"),
    ("Dental Corner", "https://dentalcorner.rs/"),
    ("Dental Serbia", "https://dentalserbia.com/"),
    ("Belgrade Dental", "https://belgradedental.com/"),
    ("Stomatologija Dr Bede", "https://drbede.com/"),
    ("Ordinacija Barjaktarevic", "https://barjaktarevic.rs/"),
    ("Lav Dental", "https://lavdental.rs/"),
    ("Dr Ast Dental", "https://drast.rs/"),
    
    # Architects & Interior Design
    ("Remorker Architects", "https://remorker.rs/"),
    ("Fluid Arhitektura", "https://fluid.rs/"),
    ("Architehna", "https://architehna.rs/"),
    ("Polyplan Arhitekti", "https://polyplan.rs/"),
    ("Bureau Cube Partners", "https://bureaucube.com/"),
    ("Dva Studio", "https://dvastudio.rs/"),
    ("Studio MM", "https://studiomm.rs/"),
    ("Spatial Design", "https://spatialdesign.rs/"),
    ("INKa Studio", "https://inkastudio.rs/"),
    ("Studio OBE", "https://studioobe.rs/"),
    ("Line 4 Design", "https://line4design.rs/"),
    ("Studio Autori", "https://autori.rs/"),
    ("Antipod Studio", "https://antipod.rs/"),
    ("Takt Studio", "https://taktstudio.rs/"),
    ("Studio Simovic", "https://studiosimovic.com/"),
    ("Arhitektonski studio Linear", "https://linear.rs/"),
    ("Proaspekt", "https://proaspekt.com/"),
    ("Synthesis Quatro", "https://sq.rs/"),
    ("Paripovic Arhitekti", "https://paripovic.rs/"),
    ("Studio Domino", "https://dominostudio.rs/"),

    # Heat pumps & Solar / Heating
    ("Eko Solar", "https://ekosolar.rs/"),
    ("Solaris Energy", "https://solaris-energy.rs/"),
    ("Gree Srbija", "https://gree.rs/"),
    ("Eko Step Pellet", "https://ekosteppellet.rs/"),
    ("Helios Solar", "https://helios-solar.rs/"),
    ("Telefon Inzenjering", "https://telefon-inzenjering.co.rs/"),
    ("Solarni Paneli SRB", "https://solarnipaneli.org/"),
    ("Master Solar", "https://mastersolar.rs/"),
    ("Klima M", "https://klimam.rs/"),
    ("Clima Calda", "https://climacalda.rs/"),
    ("Delta Term", "https://deltaterm.com/"),
    ("Termo Servis", "https://termoservis.rs/"),
    ("Alfa Plam", "https://alfaplam.rs/"),
    ("Cini Cacak", "https://cini.rs/"),
    ("Toplotne Pumpe Srbija", "https://toplotnepumpe.rs/"),
    ("Eko Toplotne Pumpe", "https://ekotoplotnepumpe.rs/"),

    # Medical clinics / Esthetics / Diagnostics
    ("Atlas Bolnica", "https://atlasopstabolnica.com/"),
    ("Euromedik", "https://euromedik.rs/"),
    ("Poliklinika Antamedica", "https://antamedica.com/"),
    ("Bel Prime Clinic", "https://belprime.rs/"),
    ("Bolnica Parks", "https://parks.rs/"),
    ("Klinika Svjetlost BG", "https://svjetlost.rs/"),
    ("Medikom", "https://medikompoliklinika.com/"),
    ("Poliklinika Roncevic", "https://poliklinikaroncevic.com/"),
    ("Poliklinika Gracia Medika", "https://graciamedika.com/"),
    ("Euro Medika", "https://euromedika.rs/"),
    ("Medical Centar", "https://medicalcentar.rs/")
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
                    if not any(x in ec for x in ['sentry', 'wix', 'example', 'domain', 'schema', 'test', 'bootstrap', 'wordpress', 'cloudflare', 'contact@yourdomain']):
                        if ec not in history:
                            valid.append(ec)
            if valid:
                return {"name": name, "url": url, "email": valid[0]}
    except Exception:
        pass
    return None

found_leads = []
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(fetch_email, item) for item in candidate_domains]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads.append(res)
            print(f"FOUND: {res['name']} -> {res['email']}")
            sys.stdout.flush()

print(f"Total leads found: {len(found_leads)}")
with open("scratch/fresh_leads.json", "w", encoding="utf-8") as f:
    json.dump(found_leads, f, ensure_ascii=False, indent=2)
