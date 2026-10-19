import sys, os, glob, re, urllib.request, json
sys.path.insert(0, 'src')
sys.path.insert(0, '.')
from outreach import mailer
from src.classes.Outreach import Outreach

with open('.mp/sent_emails_history.txt', 'r', encoding='utf-8') as f:
    hist = {l.strip().lower() for l in f if l.strip()}

browser_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

found = []
seen = set()

for p in sorted(glob.glob('scripts/test_*.py') + glob.glob('scripts/qualify_*.py')):
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    matches = re.findall(r'[\'"](?:name|company)[\'"]\s*:\s*[\'"]([^\'"]+)[\'"]\s*,\s*[\'"]url[\'"]\s*:\s*[\'"]([^\'"]+)[\'"]\s*,\s*[\'"]email[\'"]\s*:\s*[\'"]([^\'"]+)[\'"]', content)
    for name, u, em in matches:
        em = em.strip().lower()
        u = u.strip()
        dom = u.split('//')[-1].split('/')[0].replace('www.', '').lower()
        if em in hist or dom in hist:
            continue
        if em in seen:
            continue
        seen.add(em)
        found.append((name, u, em))

print(f"Total candidate matches not in history: {len(found)}")

o = Outreach()
verified = []
for name, u, em in found:
    if len(verified) >= 10:
        break
    try:
        req = urllib.request.Request(u, headers=browser_headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status != 200:
                continue
    except Exception:
        continue
    
    if not o.is_valid_mx(em):
        continue

    if mailer.verify_mailbox_smtp(em, 'ivanbradic.biz@gmail.com'):
        print(f"[VERIFIED]: {name} | {u} | {em}")
        verified.append({'company': name, 'url': u, 'email': em})

print(f"Total newly verified: {len(verified)}")
with open('.mp/qualified_batch74.json', 'w', encoding='utf-8') as f:
    json.dump(verified, f, indent=2)
