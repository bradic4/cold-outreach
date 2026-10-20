import sys
import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classes.Outreach import Outreach
from outreach.mailer import verify_mailbox_smtp

candidates = [
    {
        "company": "Top Notch Interiors",
        "url": "https://topnotchkb.co.uk",
        "email": "design@topnotchkb.co.uk",
        "role": "Bespoke Fitted Kitchens & Bathrooms Essex UK"
    },
    {
        "company": "Beckingham Designs",
        "url": "https://beckinghamdesigns.co.uk",
        "email": "hello@beckinghamdesigns.co.uk",
        "role": "Handmade Bespoke Kitchens & Living Spaces Essex UK"
    },
    {
        "company": "Raw Cabinetry",
        "url": "https://rawcabinetry.co.uk",
        "email": "info@rawcabinetry.co.uk",
        "role": "Bespoke Handcrafted Kitchens & Interiors Kent UK"
    },
    {
        "company": "Chamber Furniture",
        "url": "https://chamberfurniture.co.uk",
        "email": "info@chamberfurniture.co.uk",
        "role": "Luxury Handmade Bespoke Kitchens Kent UK"
    },
    {
        "company": "Kitchens Bespoke",
        "url": "https://kitchensbespoke.co.uk",
        "email": "info@kitchensbespoke.co.uk",
        "role": "Bespoke Fitted Kitchen Design East Grinstead West Sussex UK"
    },
    {
        "company": "Sebastian's Kitchens",
        "url": "https://sebastianskitchens.co.uk",
        "email": "info@sebastianskitchens.co.uk",
        "role": "Hand-built Bespoke Working Kitchens Chichester West Sussex UK"
    },
    {
        "company": "Tim Jasper",
        "url": "https://timjasper.co.uk",
        "email": "info@timjasper.co.uk",
        "role": "Handcrafted Bespoke Kitchens Goodwood West Sussex UK"
    },
    {
        "company": "Acorn Bespoke",
        "url": "https://bespokebyacorn.co.uk",
        "email": "info@bespokebyacorn.co.uk",
        "role": "Bespoke Carpentry & Kitchens Horsham West Sussex UK"
    },
    {
        "company": "Rever Kitchens",
        "url": "https://reverkitchens.co.uk",
        "email": "info@reverkitchens.co.uk",
        "role": "Custom Bespoke Kitchens Brighton & Hove Sussex UK"
    }
]

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as hf:
        sent_history = {line.strip().lower() for line in hf if line.strip()}

print(f"Total sent emails in history: {len(sent_history)}")

outreach = Outreach()
qualified = []

for c in candidates:
    email = c["email"].lower().strip()
    domain = c["url"].split("//")[-1].split("/")[0].replace("www.", "").lower().strip()

    print(f"\n--- Checking {c['company']} ({email}) ---")

    if email in sent_history:
        print(f"FAILED: Email already in history: {email}")
        continue
    if domain in sent_history:
        print(f"FAILED: Domain already in history: {domain}")
        continue

    # 1. HTTP 200
    try:
        r = requests.get(c["url"], timeout=10, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, verify=False)
        if r.status_code >= 400:
            print(f"FAILED HTTP status {r.status_code}")
            continue
        print(f"HTTP 200 OK (final url: {r.url})")
    except Exception as e:
        print(f"FAILED HTTP request: {e}")
        continue

    # 2. DNS MX
    if not outreach.is_valid_mx(email):
        print(f"FAILED MX for {email}")
        continue
    print(f"MX Record OK for {email}")

    # 3. SMTP Mailbox Probe
    smtp_ok = verify_mailbox_smtp(email, sender_addr="ivanbradic46@gmail.com")
    if not smtp_ok:
        print(f"FAILED SMTP probe for {email}")
        continue
    print(f"SMTP OK for {email}")

    qualified.append(c)

print("\n==========================================")
print(f"QUALIFIED COUNT: {len(qualified)}")
for q in qualified:
    print(f"- {q['company']} | {q['url']} | {q['email']}")
