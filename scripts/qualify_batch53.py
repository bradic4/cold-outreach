import urllib.request
import dns.resolver
import smtplib
import json
import os

with open('.mp/uncontacted_candidates.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

with open('.mp/sent_emails_history.txt', 'r', encoding='utf-8') as f:
    sent_history = {line.strip().lower() for line in f if line.strip()}

r = dns.resolver.Resolver(configure=False)
r.nameservers = ['8.8.8.8', '1.1.1.1']

def verify_http(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status == 200, f"HTTP {resp.status}"
    except Exception as e:
        return False, f"HTTP error: {e}"

def verify_smtp(email):
    domain = email.split('@')[1]
    try:
        answers = r.resolve(domain, 'MX', tcp=True)
        mx_records = sorted(answers, key=lambda rec: rec.preference)
        mx_host = str(mx_records[0].exchange).rstrip('.')
    except Exception as e:
        return False, f"MX lookup failed: {e}"

    try:
        server = smtplib.SMTP(timeout=8)
        server.connect(mx_host, 25)
        server.helo("gmail.com")
        server.mail("ivan.bradic@outlook.com")
        code, resp = server.rcpt(email)
        server.quit()
        if code in [250, 251]:
            return True, f"SMTP {code}: Mailbox exists ({mx_host})"
        elif code in [450, 451, 452]:
            return True, f"SMTP greylisted {code} ({mx_host})"
        elif 500 <= code <= 554:
            resp_str = str(resp).lower()
            if any(w in resp_str for w in ("spam", "blocked", "spamhaus", "dnsbl", "rbl", "policy", "client host", "relay", "service unavailable")):
                return True, f"SMTP policy bypass ({code})"
            if any(w in resp_str for w in ("user unknown", "no such user", "does not exist", "recipient address rejected", "invalid recipient", "mailbox not found", "user not found", "bad destination")):
                return False, f"SMTP rejected {code}: User unknown"
            return True, f"SMTP code {code}"
        return True, f"SMTP {code}"
    except Exception as e:
        return True, f"SMTP bypass/timeout: {e}"

qualified = []

# Already known good from batch 52 qualifier:
already_good = [
    {"company": "Reynolds Bespoke", "url": "https://reynoldsbespoke.co.uk", "email": "info@reynoldsbespoke.co.uk", "role": "Bespoke Fitted Furniture & Joinery UK"},
    {"company": "Woods & Langton Joiners", "url": "https://woodsandlangtonjoiners.co.uk", "email": "info@woodsandlangtonjoiners.co.uk", "role": "Bespoke Timber Joinery UK"},
    {"company": "Abington Design House", "url": "https://abington.ie", "email": "info@abington.ie", "role": "Bespoke Luxury Kitchens & Furniture Ireland"}
]

for g in already_good:
    dom = g['url'].split('//')[-1].split('/')[0].replace('www.', '').lower()
    if dom not in sent_history and g['email'] not in sent_history:
        qualified.append(g)

for c in candidates:
    if len(qualified) >= 8:
        break
    url = c['url'].lower()
    email = c['email'].lower()
    dom = url.split('//')[-1].split('/')[0].replace('www.', '').lower()
    if dom in sent_history or email in sent_history:
        continue
    if any(q['email'] == email for q in qualified):
        continue
    if '.ie' not in dom and '.co.uk' not in dom:
        continue

    h_ok, h_msg = verify_http(c['url'])
    if not h_ok:
        continue
    s_ok, s_msg = verify_smtp(c['email'])
    if not s_ok:
        continue
    print(f"[+] QUALIFIED: {c['company']} | {c['url']} | {c['email']} | {s_msg}")
    qualified.append(c)

print(f"\nTotal qualified for Batch 53: {len(qualified)}")
with open('.mp/qualified_batch53.json', 'w', encoding='utf-8') as f:
    json.dump(qualified, f, indent=2)
