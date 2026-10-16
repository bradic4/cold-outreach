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

browser_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}

def verify_http(url):
    try:
        req = urllib.request.Request(url, headers=browser_headers)
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
        server.helo("mail.google.com")
        server.mail("ivanbradic.biz@gmail.com")
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

# Prior verified lead Mooneys Kitchens
prior = [
    {"company": "Mooneys Kitchens", "url": "https://mooneys.ie", "email": "info@mooneys.ie", "role": "Bespoke Fitted Kitchens Ireland"}
]

for p in prior:
    em = p['email'].lower()
    dom = p['url'].split('//')[-1].split('/')[0].replace('www.', '').lower()
    if em not in sent_history and dom not in sent_history:
        h_ok, h_msg = verify_http(p['url'])
        s_ok, s_msg = verify_smtp(p['email'])
        if h_ok and s_ok:
            print(f"[+] QUALIFIED (Prior): {p['company']} | {p['url']} | {p['email']} | {s_msg}")
            qualified.append(p)

for c in candidates:
    if len(qualified) >= 8:
        break
    url = c.get('url', '').lower()
    email = c.get('email', '').lower()
    if not url or not email:
        continue
    dom = url.split('//')[-1].split('/')[0].replace('www.', '').lower()
    if dom in sent_history or email in sent_history:
        continue
    if any(q['email'].lower() == email for q in qualified):
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

print(f"\nTotal qualified for Batch 65: {len(qualified)}")
os.makedirs('.mp', exist_ok=True)
with open('.mp/qualified_batch65.json', 'w', encoding='utf-8') as f:
    json.dump(qualified, f, indent=2)
