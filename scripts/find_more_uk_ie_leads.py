import sys, os, glob, re, urllib.request, json
sys.path.insert(0, 'src')
sys.path.insert(0, '.')
from outreach import mailer
from src.classes.Outreach import Outreach

with open('.mp/sent_emails_history.txt', 'r', encoding='utf-8') as f:
    hist = {l.strip().lower() for l in f if l.strip()}

o = Outreach()
candidates = []
seen = set()

for p in sorted(glob.glob('scripts/test_*.py') + glob.glob('scripts/qualify_*.py')):
    if any(k in p for k in ['zrenjanin', 'sabac', 'smb', 'serbia']):
        continue
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
        if any(f in em for f in ['gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com', 'aol.com', 'live.com', 'msn.com', 'btinternet.com']):
            continue
        if dom.endswith('.rs') or dom.endswith('.me') or dom.endswith('.ba'):
            continue
        seen.add(em)
        candidates.append((name, u, em))

print('Total UK/IE joinery/kitchen candidates in pool:', len(candidates))

browser_headers = {'User-Agent': 'Mozilla/5.0'}
verified = []
for name, u, em in candidates:
    if len(verified) >= 8:
        break
    try:
        req = urllib.request.Request(u, headers=browser_headers)
        with urllib.request.urlopen(req, timeout=4) as r:
            if r.status != 200:
                continue
    except Exception:
        continue
    
    if o.is_valid_mx(em) and mailer.verify_mailbox_smtp(em, 'ivanbradic.biz@gmail.com'):
        print(f'VERIFIED UK/IE: {name} | {u} | {em}')
        verified.append({'company': name, 'url': u, 'email': em})

print('Total verified UK/IE:', len(verified))
with open('.mp/qualified_batch76_uk_ie.json', 'w', encoding='utf-8') as f:
    json.dump(verified, f, indent=2)
