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

candidate_domains_3 = [
    # Dental clinics / Dental tourism
    ("Stomatoloska ordinacija Dr Veselinovic", "https://drveselinovic.rs/"),
    ("Ordinacija Dentib", "https://dentib.rs/"),
    ("Dr Lopandic Dental", "https://drlopandic.rs/"),
    ("Stomatologija Kruna Krunic", "https://krunakrunic.com/"),
    ("Stomatoloska ordinacija Vukovic", "https://ordinacijavukovic.rs/"),
    ("Dental Studio Magic", "https://dentalmagic.rs/"),
    ("Dentus Perfectus", "https://dentusperfectus.rs/"),
    ("Ordinacija Dentalis", "https://dentalis.rs/"),
    ("Stomatoloska ordinacija Smile Time", "https://smiletime.rs/"),
    ("Zubarska ordinacija Dr Minic", "https://drminic.rs/"),
    ("Dental Corner Esthetics", "https://dentalcorner.rs/"),
    ("Ordinacija Dr Scepano", "https://drscepano.rs/"),
    ("Stomatologija Pavlovic", "https://stomatologijapavlovic.rs/"),
    ("Dental Serbia Info", "https://dentalserbia.com/"),
    ("Implant Centar Beograd", "https://implantcentar.rs/"),
    ("Ordinacija Dr Vranjes", "https://drvranjes.rs/"),
    ("Stomatoloski Centar Bobic", "https://dentalcentarbobic.rs/"),
    ("Modest Dental Centar", "https://modestdental.rs/"),
    ("Ordinacija Lav Dental", "https://lavdental.rs/"),
    ("Dr Ast Dental Centar", "https://drast.rs/"),

    # Architects & Interior Design
    ("Arhitektonski studio Linear", "https://linear.rs/"),
    ("Proaspekt Arhitekti", "https://proaspekt.com/"),
    ("Paripovic Arhitekti", "https://paripovic.rs/"),
    ("Studio Domino", "https://dominostudio.rs/"),
    ("Studio Alfirevic", "https://alfirevic.com/"),
    ("Kuzmanov and Partners", "https://kuzmanovandpartners.com/"),
    ("Studio Simovic", "https://studiosimovic.com/"),
    ("Takt Studio", "https://taktstudio.rs/"),
    ("Antipod Studio", "https://antipod.rs/"),
    ("INKa Studio", "https://inkastudio.rs/"),
    ("Spatial Design", "https://spatialdesign.rs/"),
    ("Studio OBE", "https://studioobe.rs/"),
    ("Line 4 Design", "https://line4design.rs/"),
    ("Arhitektonski biro DA Dizajn", "https://dadizajn.rs/"),
    ("Inka Studio Beograd", "https://inkastudio.rs/"),
    ("Studio Metar", "https://studiometar.rs/"),
    ("Architehna Biro", "https://architehna.rs/"),

    # Heating & Solar
    ("Solaris Energy Srbija", "https://solaris-energy.rs/"),
    ("Helios Solar Sistemi", "https://helios-solar.rs/"),
    ("Telefon Inzenjering Solar", "https://telefon-inzenjering.co.rs/"),
    ("Klima M Grejanje", "https://klimam.rs/"),
    ("Clima Calda Pumpe", "https://climacalda.rs/"),
    ("Delta Term Grejanje", "https://deltaterm.com/"),
    ("Termo Servis", "https://termoservis.rs/"),
    ("Eko Toplotne Pumpe", "https://ekotoplotnepumpe.rs/"),
    ("Solar Star Srbija", "https://solarstar.rs/"),
    ("Solar Mont", "https://solarmont.rs/"),
    ("Klima BG", "https://klimabg.rs/"),
    ("Termokon", "https://termokon.rs/"),
    ("Frigooprema", "https://frigooprema.rs/"),
    ("Termoprojekt", "https://termoprojekt.com/"),

    # Medical clinics / Esthetics / Diagnostics
    ("Poliklinika Roncevic", "https://poliklinikaroncevic.com/"),
    ("Poliklinika Gracia Medika", "https://graciamedika.com/"),
    ("Euro Medika Centar", "https://euromedika.rs/"),
    ("Bel Prime Clinic", "https://belprime.rs/"),
    ("Bolnica Sveti Jovan", "https://svetijovan.rs/"),
    ("Klinika Perinatal", "https://perinatal.rs/"),
    ("Poliklinika Pekic", "https://poliklinikapekic.com/"),
    ("Poliklinika Nada D", "https://poliklinikanadad.rs/"),
    ("Klinika Genesis", "https://genesis.rs/"),
    ("Poliklinika Human", "https://poliklinikahuman.rs/"),
    ("Poliklinika Kragujmedik", "https://kragujmedik.rs/"),
    ("Poliklinika Novamed", "https://novamed.rs/"),
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

found_leads_3 = []
with ThreadPoolExecutor(max_workers=12) as executor:
    futures = [executor.submit(fetch_email, item) for item in candidate_domains_3]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_3.append(res)
            print(f"FOUND: {res['name']} -> {res['email']}")
            sys.stdout.flush()

print(f"Total leads found in round 3: {len(found_leads_3)}")
with open("scratch/fresh_leads_3.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_3, f, ensure_ascii=False, indent=2)
