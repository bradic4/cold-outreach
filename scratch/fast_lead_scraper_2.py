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

candidate_domains_2 = [
    ("Ordinacija Barjaktarevic Dental", "https://barjaktarevic.rs/"),
    ("Dr Ast Stomatologija", "https://drast.rs/"),
    ("Dental Magic", "https://dentalmagic.rs/"),
    ("Implant Studio BG", "https://implantstudio.rs/"),
    ("Lav Dental Ordinacija", "https://lavdental.rs/"),
    ("Dental Serbia Centar", "https://dentalserbia.com/"),
    ("Ordinacija Pavlovic Zubar", "https://stomatologijapavlovic.rs/"),
    ("Modest Dental Klinika", "https://modestdental.rs/"),
    ("Dental Centar Bobic", "https://dentalcentarbobic.rs/"),
    ("Ordinacija Vukovic", "https://ordinacijavukovic.rs/"),
    ("Stomatologija Kruna Krunic", "https://krunakrunic.com/"),
    ("Dentalis Art", "https://dentalisart.rs/"),
    ("Dental Centar Nis", "https://dentalcentarnis.rs/"),
    ("Moji Zubari", "https://mojizubari.rs/"),

    # Architects
    ("Arhitektonski studio Linear", "https://linear.rs/"),
    ("Proaspekt Arhitektura", "https://proaspekt.com/"),
    ("Paripovic Arhitekti", "https://paripovic.rs/"),
    ("Studio Domino Enterijeri", "https://dominostudio.rs/"),
    ("Studio Alfirevic Arhitektura", "https://alfirevic.com/"),
    ("Arhi.pro", "https://arhipro.com/"),
    ("Kuzmanov and Partners", "https://kuzmanovandpartners.com/"),
    ("Studio Simovic Arhitekti", "https://studiosimovic.com/"),
    ("Takt Studio Arhitektura", "https://taktstudio.rs/"),
    ("Antipod Design", "https://antipod.rs/"),
    ("INKa Studio Beograd", "https://inkastudio.rs/"),
    ("Spatial Design Enterijeri", "https://spatialdesign.rs/"),

    # Solar & Heating
    ("Solaris Energy Srbija", "https://solaris-energy.rs/"),
    ("Helios Solar Sistemi", "https://helios-solar.rs/"),
    ("Telefon Inzenjering Solar", "https://telefon-inzenjering.co.rs/"),
    ("Solarni Paneli SRB Org", "https://solarnipaneli.org/"),
    ("Klima M Grejanje", "https://klimam.rs/"),
    ("Clima Calda Pumpe", "https://climacalda.rs/"),
    ("Delta Term Grejanje", "https://deltaterm.com/"),
    ("Termo Servis Toplota", "https://termoservis.rs/"),
    ("Alfa Plam Vranje", "https://alfaplam.rs/"),
    ("Eko Toplotne Pumpe BG", "https://ekotoplotnepumpe.rs/"),
    ("Solar Star Srbija", "https://solarstar.rs/"),
    ("Solar Mont", "https://solarmont.rs/"),
    ("Energy Net Solari", "https://energynet.rs/"),
    ("Viessmann Beograd", "https://viessmann.rs/"),

    # Clinics & Aesthetics
    ("Poliklinika Roncevic Beograd", "https://poliklinikaroncevic.com/"),
    ("Poliklinika Gracia Medika", "https://graciamedika.com/"),
    ("Euro Medika Centar", "https://euromedika.rs/"),
    ("Bel Prime Clinic Vracar", "https://belprime.rs/"),
    ("Poliklinika Cardios", "https://cardios.rs/"),
    ("Bolnica Sveti Jovan", "https://svetijovan.rs/"),
    ("Klinika Perinatal", "https://perinatal.rs/"),
    ("Poliklinika Pekic", "https://poliklinikapekic.com/")
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

found_leads_2 = []
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(fetch_email, item) for item in candidate_domains_2]
    for future in as_completed(futures):
        res = future.result()
        if res:
            found_leads_2.append(res)
            print(f"FOUND 2: {res['name']} -> {res['email']}")
            sys.stdout.flush()

print(f"Batch 2 found: {len(found_leads_2)}")
with open("scratch/fresh_leads_2.json", "w", encoding="utf-8") as f:
    json.dump(found_leads_2, f, ensure_ascii=False, indent=2)
