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

# Target UK and Ireland specific files
uk_ie_files = [
    'scripts/test_cornwall.py',
    'scripts/test_devon.py',
    'scripts/test_somerset.py',
    'scripts/test_glos.py',
    'scripts/test_leeds.py',
    'scripts/test_hants_candidates.py',
    'scripts/test_cork_dublin.py',
    'scripts/test_galway.py',
    'scripts/test_kerry.py',
    'scripts/test_kerry_batch44.py',
    'scripts/test_kildare.py',
    'scripts/test_kildare_offaly.py',
    'scripts/test_louth_westmeath.py',
    'scripts/test_meath.py',
    'scripts/test_waterford.py',
    'scripts/test_wicklow.py',
    'scripts/test_clare.py',
    'scripts/test_sligo_clare.py',
    'scripts/test_batch47_uk.py',
    'scripts/test_batch47_ireland.py',
    'scripts/test_batch32_candidates3.py',
    'scripts/test_batch32_candidates4.py',
    'scripts/test_batch32_candidates5.py',
    'scripts/test_batch34_candidates.py',
    'scripts/test_batch35_candidates.py',
    'scripts/test_batch36_candidates.py',
    'scripts/test_batch37_candidates.py',
    'scripts/test_batch38_candidates.py',
    'scripts/test_batch42_candidates.py',
    'scripts/test_batch43_candidates.py',
    'scripts/test_batch44_candidates.py',
    'scripts/test_batch45_candidates.py',
    'scripts/test_batch46_candidates.py',
    'scripts/test_batch47_candidates.py',
    'scripts/test_batch48_candidates.py',
    'scripts/test_batch49_candidates.py',
    'scripts/test_batch50_candidates.py'
]

for p in uk_ie_files:
    if not os.path.exists(p):
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
        seen.add(em)
        candidates.append((name, u, em))

print(f'Total candidates from UK/IE regional files: {len(candidates)}')

browser_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
verified = []
for name, u, em in candidates:
    if len(verified) >= 10:
        break
    try:
        req = urllib.request.Request(u, headers=browser_headers)
        with urllib.request.urlopen(req, timeout=4) as r:
            if r.status != 200:
                continue
    except Exception:
        continue
    
    if not o.is_valid_mx(em):
        continue

    if mailer.verify_mailbox_smtp(em, 'ivanbradic.biz@gmail.com'):
        print(f'[VERIFIED UK/IE]: {name} | {u} | {em}')
        verified.append({'company': name, 'url': u, 'email': em})

print(f'Total newly verified UK/IE: {len(verified)}')
with open('.mp/qualified_batch77.json', 'w', encoding='utf-8') as f:
    json.dump(verified, f, indent=2)
