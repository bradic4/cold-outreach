import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classes.Outreach import Outreach
from outreach.mailer import verify_mailbox_smtp

candidates = [
    {
        "company": "Finlay Kitchens",
        "url": "https://finlaykitchens.com",
        "email": "info@finlaykitchens.com",
        "role": "Bespoke Fitted Kitchens Galway Ireland"
    },
    {
        "company": "Edition Kitchens",
        "url": "https://editionkitchens.ie",
        "email": "info@editionkitchens.ie",
        "role": "Contemporary Bespoke Kitchens Dungarvan Waterford Ireland"
    },
    {
        "company": "Galleywood Kitchens",
        "url": "https://galleywoodkitchenstudio.co.uk",
        "email": "mail@galleywoodkitchens.com",
        "role": "Bespoke Kitchen Design Chelmsford Essex UK"
    },
    {
        "company": "Brentwood Kitchen & Interiors",
        "url": "https://brentwoodkai.com",
        "email": "info@brentwoodkai.com",
        "role": "Luxury Bespoke Kitchens Brentwood Essex UK"
    },
    {
        "company": "CEK Kitchens",
        "url": "https://cek.online",
        "email": "info@cek.online",
        "role": "Handmade Bespoke Kitchens Colchester Essex UK"
    },
    {
        "company": "Square & True",
        "url": "https://squareandtrue.uk",
        "email": "hello@squareandtrue.uk",
        "role": "Bespoke Kitchens & Cabinetry Essex UK"
    },
    {
        "company": "K2B Bespoke Kitchens",
        "url": "https://k2bbespokekitchens.co.uk",
        "email": "info@k2bbespokekitchens.co.uk",
        "role": "Handcrafted Luxury Kitchens Bury St Edmunds UK"
    },
    {
        "company": "Behm Kitchens",
        "url": "https://behmkitchens.co.uk",
        "email": "hello@behmkitchens.co.uk",
        "role": "Bespoke Kitchens & Joinery Norwich Norfolk UK"
    }
]

outreach = Outreach()

# Load history
history = set()
if os.path.exists(".mp/sent_emails_history.txt"):
    with open(".mp/sent_emails_history.txt", "r", encoding="utf-8") as f:
        for line in f:
            em = line.strip().lower()
            if em:
                history.add(em)

print(f"Total sent emails in history: {len(history)}")

qualified = []
for c in candidates:
    email = c["email"].lower().strip()
    url = c["url"]
    print(f"\n--- Checking {c['company']} ({email}) ---")
    if email in history:
        print(f"FAILED: Email already in history: {email}")
        continue
    
    # HTTP check
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, verify=False)
        if r.status_code != 200:
            print(f"FAILED HTTP: status {r.status_code}")
            continue
        print(f"HTTP 200 OK (final url: {r.url})")
    except Exception as e:
        print(f"FAILED HTTP: {e}")
        continue

    # MX check
    has_mx = outreach.is_valid_mx(email)
    if not has_mx:
        print(f"FAILED MX: No MX records for {email}")
        continue
    print(f"MX Record OK for {email}")

    # SMTP check
    smtp_ok = verify_mailbox_smtp(email, sender_addr="ivanbradic.biz@gmail.com")
    if not smtp_ok:
        print(f"FAILED SMTP: Mailbox probe failed for {email}")
        continue
    print(f"SMTP OK for {email}")

    qualified.append(c)

print(f"\n==========================================")
print(f"QUALIFIED COUNT: {len(qualified)}")
for q in qualified:
    print(f"- {q['company']} | {q['url']} | {q['email']}")
