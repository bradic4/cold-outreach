import urllib.request
import urllib.parse
import re
import json
import os
import smtplib
import dns.resolver

with open(".mp/sent_emails_history.txt", "r", encoding="utf-8") as f:
    sent_history = {line.strip().lower() for line in f if line.strip()}

with open(".mp/outlook_search_candidates.json", "r", encoding="utf-8") as f:
    urls = json.load(f)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}

def get_html(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status, resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return None, str(e)

def extract_emails(html):
    # Find mailto: or regex
    mails = set(re.findall(r'href=[\'"]mailto:([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)[\'"]', html, re.I))
    text_mails = set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', html))
    all_m = mails.union(text_mails)
    # clean
    clean = set()
    for m in all_m:
        m = m.lower().strip()
        if not any(m.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".js", ".css"]):
            if "sentry" not in m and "wix" not in m and "domain" not in m and "example" not in m:
                clean.add(m)
    return clean

def verify_smtp(email):
    domain = email.split('@')[1]
    try:
        r = dns.resolver.Resolver(configure=False)
        r.nameservers = ['8.8.8.8', '1.1.1.1']
        answers = r.resolve(domain, 'MX', tcp=True)
        mx_records = sorted(answers, key=lambda r: r.preference)
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
                return True, f"SMTP spam policy ({code})"
            if any(w in resp_str for w in ("user unknown", "no such user", "does not exist", "recipient address rejected", "invalid recipient", "mailbox not found", "user not found", "bad destination")):
                return False, f"SMTP rejected {code}: User unknown"
            return True, f"SMTP code {code}"
        return True, f"SMTP {code}"
    except Exception as e:
        return True, f"SMTP bypass/timeout: {e}"

results = []

for u in urls:
    dom = u.split("//")[-1].replace("www.", "").lower()
    if dom in sent_history:
        print(f"[-] Domain {dom} already in sent history, skipping")
        continue

    status, html = get_html(u)
    if status != 200:
        print(f"[-] {u} returned status {status}")
        continue

    # title
    m = re.search(r'<title>(.*?)</title>', html, re.I)
    title = m.group(1).strip() if m else dom

    emails = extract_emails(html)
    if not emails:
        # try contact page
        for sub in ["/contact", "/contact-us", "/get-in-touch"]:
            c_status, c_html = get_html(u.rstrip("/") + sub)
            if c_status == 200:
                emails.update(extract_emails(c_html))
                if emails:
                    break

    # filter out emails in sent_history
    fresh_emails = [e for e in emails if e not in sent_history]
    if not fresh_emails:
        print(f"[-] {u}: no fresh email found (found: {emails})")
        continue

    # choose best email (prefer info@, hello@, sales@, enquiries@, or company domain)
    chosen_email = None
    for pref in ["info@", "enquiries@", "hello@", "sales@", "contact@", "office@"]:
        for e in fresh_emails:
            if e.startswith(pref):
                chosen_email = e
                break
        if chosen_email:
            break
    if not chosen_email:
        chosen_email = list(fresh_emails)[0]

    # SMTP check
    ok, reason = verify_smtp(chosen_email)
    print(f"[?] Checking {u} -> {chosen_email} : {reason}")
    if not ok:
        print(f"[-] SMTP rejected {chosen_email}")
        continue

    # extract clean company name
    clean_name = title.split("|")[0].split("-")[0].split("–")[0].split(":")[0].strip()
    if len(clean_name) > 35 or len(clean_name) < 3:
        clean_name = dom.split(".")[0].replace("-", " ").title()

    results.append({
        "company": clean_name,
        "url": u,
        "email": chosen_email,
        "title": title,
        "smtp_status": reason
    })
    print(f"[+] QUALIFIED: {clean_name} | {u} | {chosen_email}")
    if len(results) >= 8:
        break

print(f"\nTotal qualified leads: {len(results)}")
with open(".mp/qualified_batch51.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
