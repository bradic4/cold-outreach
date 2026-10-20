import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classes.Outreach import Outreach
from outreach.mailer import verify_mailbox_smtp

candidates = [
    {
        "company": "Albany Kitchens",
        "url": "https://www.albanykitchens.co.uk",
        "email": "info@albanykitchens.co.uk",
        "role": "Bespoke Kitchen Design Bishop's Stortford Hertfordshire UK"
    },
    {
        "company": "Symphony Kitchens",
        "url": "https://www.symphonykitchens.ie",
        "email": "info@symphonykitchens.ie",
        "role": "Bespoke Fitted Kitchens Castlebar Mayo Ireland"
    },
    {
        "company": "Planit Interiors",
        "url": "https://planit-interiors.co.uk",
        "email": "sales@planit-interiors.co.uk",
        "role": "Bespoke Kitchen Design Loughborough Leicestershire UK"
    },
    {
        "company": "Sherwin Hall Kitchens",
        "url": "https://sherwinhall.com",
        "email": "sales@sherwinhall.co.uk",
        "role": "Handmade Bespoke Kitchens Oadby Leicestershire UK"
    },
    {
        "company": "Luxe Kitchen Designs",
        "url": "https://luxekitchendesigns.co.uk",
        "email": "info@luxekitchendesigns.co.uk",
        "role": "Bespoke Kitchen Design Leicestershire UK"
    },
    {
        "company": "Bespoke Trade Kitchens",
        "url": "https://bespoketradekitchens.co.uk",
        "email": "sales@bespoketradekitchens.co.uk",
        "role": "Custom Bespoke Kitchens Leicester UK"
    },
    {
        "company": "Kenton Jones",
        "url": "https://kentonjones.com",
        "email": "sales@kentonjones.com",
        "role": "Bespoke Handmade Kitchens & Furniture Shropshire UK"
    },
    {
        "company": "Kitchen Visions",
        "url": "https://kitchenvisions.co.uk",
        "email": "tony@kitchenvisions.co.uk",
        "role": "Bespoke Fitted Kitchens Newport Shropshire UK"
    },
    {
        "company": "RJ Evans Cabinet Maker",
        "url": "https://rjevanscabinetmaker.co.uk",
        "email": "hello@rjevanscabinetmaker.co.uk",
        "role": "Bespoke Cabinet Maker & Kitchens Shrewsbury Shropshire UK"
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
