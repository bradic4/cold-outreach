import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classes.Outreach import Outreach
from outreach.mailer import verify_mailbox_smtp

candidates = [
    {
        "company": "Kitchen Visions",
        "url": "https://www.kitchenvisions.co.uk",
        "email": "tony@kitchenvisions.co.uk",
        "role": "Bespoke Fitted Kitchens Newport Shropshire UK"
    },
    {
        "company": "RJ Evans Cabinet Maker",
        "url": "https://rjevanscabinetmaker.co.uk",
        "email": "hello@rjevanscabinetmaker.co.uk",
        "role": "Bespoke Cabinet Maker & Kitchens Shrewsbury Shropshire UK"
    },
    {
        "company": "Ascot Bespoke Kitchens",
        "url": "https://abkkitchens.co.uk",
        "email": "derby@abkkitchens.co.uk",
        "role": "Bespoke Made-to-Measure Kitchens Derby UK"
    },
    {
        "company": "Bathroom & Kitchen Solutions",
        "url": "https://bathroomandkitchensolutions.co.uk",
        "email": "hello@bathroomandkitchensolutions.co.uk",
        "role": "Luxury Custom Cabinetry & Kitchens Nottinghamshire UK"
    },
    {
        "company": "UK Kitchens",
        "url": "https://ukkitchens.co.uk",
        "email": "sales@ukkitchens.co.uk",
        "role": "Bespoke Kitchens Design & Installation Nottingham UK"
    },
    {
        "company": "SB Interiors",
        "url": "https://s-binteriors.co.uk",
        "email": "rebecca@s-binteriors.co.uk",
        "role": "Bespoke Kitchen Design & Installation Nottinghamshire UK"
    },
    {
        "company": "The Devon Kitchen Company",
        "url": "https://thedevonkitchencompany.co.uk",
        "email": "hello@thedevonkitchencompany.co.uk",
        "role": "Bespoke Kitchen Design & Fitting Plymouth Devon UK"
    },
    {
        "company": "Kitchenworld Exeter",
        "url": "https://kitchenworldexeter.co.uk",
        "email": "design@kitchenworldexeter.co.uk",
        "role": "Bespoke Kitchen Design Studio Exeter Devon UK"
    },
    {
        "company": "SDC Kitchens",
        "url": "https://sdckitchens.co.uk",
        "email": "enquiries@sdckitchens.co.uk",
        "role": "Bespoke Fitted Kitchens Exeter Devon UK"
    },
    {
        "company": "Panache Interiors",
        "url": "https://panacheinteriors.co.uk",
        "email": "mark@panacheinteriors.co.uk",
        "role": "Bespoke Interior Design & Kitchens East Devon UK"
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
