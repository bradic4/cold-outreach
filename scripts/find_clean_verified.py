import json
import dns.resolver
import smtplib
import urllib.request
import os

with open('.mp/uncontacted_candidates.json', encoding='utf-8') as f:
    candidates = json.load(f)

with open('.mp/sent_emails_history.txt', encoding='utf-8') as f:
    hist = {l.strip().lower() for l in f if l.strip()}

r = dns.resolver.Resolver(configure=False)
r.nameservers = ['8.8.8.8', '1.1.1.1']

browser_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

clean = []
for c in candidates:
    em = c.get('email', '').strip().lower()
    u = c.get('url', '').strip().lower()
    if not em or not u or '@' not in em:
        continue
    dom = u.split('//')[-1].split('/')[0].replace('www.', '').lower()
    em_dom = em.split('@')[1]
    if em in hist or dom in hist:
        continue
    if '.ie' not in dom and '.co.uk' not in dom:
        continue

    # Check MX
    try:
        answers = r.resolve(em_dom, 'MX', tcp=True)
        mx_records = sorted(answers, key=lambda rec: rec.preference)
        mx_host = str(mx_records[0].exchange).rstrip('.')
    except Exception:
        continue

    # Check HTTP 200
    try:
        req = urllib.request.Request(c['url'], headers=browser_headers)
        with urllib.request.urlopen(req, timeout=4) as resp:
            if resp.status != 200:
                continue
    except Exception:
        continue

    # Strict SMTP Check
    try:
        server = smtplib.SMTP(timeout=5)
        server.connect(mx_host, 25)
        server.helo('mail.google.com')
        server.mail('ivanbradic.biz@gmail.com')
        code, resp = server.rcpt(em)
        server.quit()
        resp_str = str(resp).lower()
        if code in [250, 251]:
            print(f"[250 VALID]: {c['company']} | {em} | {c['url']}")
            clean.append(c)
        elif 500 <= code <= 554:
            if any(w in resp_str for w in ('user unknown', 'no such user', 'does not exist', 'recipient address rejected', 'invalid recipient', 'mailbox not found', 'user not found', 'bad destination', 'invalid', 'disabled')):
                continue
            if any(w in resp_str for w in ('spamhaus', 'blocked', 'dnsbl', 'rbl', 'policy', 'client host')):
                print(f"[POLICY BYPASS]: {c['company']} | {em} | {c['url']}")
                clean.append(c)
    except Exception:
        continue

    if len(clean) >= 8:
        break

print('Total clean verified:', len(clean))
os.makedirs('.mp', exist_ok=True)
with open('.mp/clean_verified.json', 'w', encoding='utf-8') as f:
    json.dump(clean, f, indent=2)
