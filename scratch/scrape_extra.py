import urllib.request
import re
import json
import ssl
import sys
import socket

sys.stdout.reconfigure(encoding='utf-8')
socket.setdefaulttimeout(3)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with open('.mp/sent_emails_history.txt', 'r', encoding='utf-8', errors='ignore') as f:
    history = set(line.strip().lower() for line in f if line.strip())

candidates = [
    ("M Enterijer Gradnja", "https://m-enterijer.rs/"),
    ("Modulor Gradnja", "https://modulor.rs/"),
    ("Grading Kragujevac", "https://grading.rs/"),
    ("Dental Spa Centar", "https://dentalspa.co.rs/"),
    ("Ordinacija Milosevic", "https://stomatologijamilosevic.rs/"),
    ("Ordinacija Dr Radojkovic", "https://drradojkovic.rs/"),
    ("Dental Studio Vuckovic", "https://dentalvuckovic.rs/"),
    ("Klima Eko Sistemi", "https://klimaeko.rs/"),
    ("Termokon Inzenjering", "https://termokon.rs/"),
    ("Poliklinika Medicor", "https://medicor.rs/"),
    ("Poliklinika Sveti Jovan", "https://svetijovan.rs/")
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

found = []
for name, url in candidates:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=3) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            raw_emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html))
            for e in raw_emails:
                ec = e.lower().strip()
                if not any(ec.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.css', '.js', '.avif')):
                    if not any(x in ec for x in ['sentry', 'wix', 'example', 'domain', 'schema', 'test', 'bootstrap', 'wordpress', 'cloudflare', 'contact@yourdomain', 'email@', 'posao', 'job']):
                        if ec not in history:
                            found.append({"name": name, "url": url, "email": ec})
                            print(f"FOUND: {name} -> {ec}")
                            break
    except Exception:
        pass

with open("scratch/fresh_leads_extra.json", "w", encoding="utf-8") as f:
    json.dump(found, f, ensure_ascii=False, indent=2)
