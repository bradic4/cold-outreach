import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classes.Outreach import Outreach
from outreach.mailer import verify_mailbox_smtp

candidates = [
    {
        "company": "Urban Kitchens",
        "url": "https://www.urbankdcni.co.uk",
        "email": "hello@urbankdcni.co.uk",
        "role": "Bespoke Contemporary Kitchens Belfast Northern Ireland"
    },
    {
        "company": "Gatt Designs",
        "url": "https://gattdesigns.co.uk",
        "email": "info@gattdesigns.co.uk",
        "role": "Bespoke Kitchen & Interior Architecture Belfast UK"
    },
    {
        "company": "Studio Four Interiors",
        "url": "https://www.studiofourinteriors.co.uk",
        "email": "info@studiofourinteriors.co.uk",
        "role": "Luxury Bespoke Kitchens Belfast Northern Ireland"
    },
    {
        "company": "So Kipling",
        "url": "https://sokipling.co.uk",
        "email": "info@sokipling.co.uk",
        "role": "Handmade Bespoke Kitchens & Cabinetry Cornwall UK"
    },
    {
        "company": "David Lisle",
        "url": "https://davidlisle.co.uk",
        "email": "email@davidlisle.co.uk",
        "role": "Luxury Bespoke Kitchen Furniture Cheshire UK"
    },
    {
        "company": "CKB Design",
        "url": "https://ckbdesign.ie",
        "email": "kitchens@ckbdesign.ie",
        "role": "Bespoke Kitchens & Living Spaces Navan Meath Ireland"
    },
    {
        "company": "Lifestyle Kitchen Design",
        "url": "https://lifestylekitchendesign.co.uk",
        "email": "enquiries@lifestylekitchendesign.co.uk",
        "role": "Bespoke Fitted Kitchens Stirling Scotland UK"
    },
    {
        "company": "Johnston Contracts",
        "url": "https://www.johnstoncontracts.co.uk",
        "email": "info@johnstoncontracts.co.uk",
        "role": "Bespoke Kitchens & Interior Joinery Lisburn UK"
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
