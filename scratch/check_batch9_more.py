import urllib.request
import re
import json
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with open('.mp/sent_emails_history.txt', 'r', encoding='utf-8', errors='ignore') as f:
    history = set(line.strip().lower() for line in f if line.strip())

check_urls = [
    ("Tehnopek Oprema", "https://tehnopek.com/"),
    ("Finans Pekarska Oprema", "https://finans.co.rs/"),
    ("Skala Garden Navodnjavanje", "https://skalagarden.com/"),
    ("Tehnicki Pregled Don", "https://tehnickipregleddon.rs/"),
    ("Laser Derma Beograd", "https://laserderma.rs/"),
    ("Kite DOO Mehanizacija", "https://kitedoo.rs/"),
    ("Skovran Mehanizacija", "https://skovran.rs/")
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for name, url in check_urls:
    for u in [url, f"{url}kontakt", f"{url}kontakt/"]:
        try:
            req = urllib.request.Request(u, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=3) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                raw = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html))
                for e in raw:
                    ec = e.lower().strip()
                    if not any(ec.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.css', '.js', '.avif')):
                        if not any(x in ec for x in ['sentry', 'wix', 'example', 'domain', 'schema', 'test', 'bootstrap', 'wordpress', 'cloudflare', 'contact@yourdomain', 'email@', 'posao', 'job', 'privacy']):
                            if ec not in history:
                                print(f"FOUND B9 MORE: {name} -> {ec}")
                                break
        except Exception:
            pass
