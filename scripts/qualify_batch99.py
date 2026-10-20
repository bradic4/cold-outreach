import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classes.Outreach import Outreach
import requests

candidates = [
    {
        "company": "Lakeland Bespoke Interiors",
        "url": "https://lakelandbespokeinteriors.co.uk",
        "email": "info@lakelandbespokeinteriors.co.uk",
        "role": "Bespoke Fitted Kitchens & Bedrooms Windermere Cumbria UK"
    },
    {
        "company": "The Secret Drawer",
        "url": "https://secret-drawer.co.uk",
        "email": "info@secret-drawer.co.uk",
        "role": "Handcrafted Bespoke Kitchens & Furniture Yorkshire UK"
    },
    {
        "company": "Skipton Joinery",
        "url": "https://skiptonjoinery.co.uk",
        "email": "info@skiptonjoinery.co.uk",
        "role": "Bespoke Kitchens & Architectural Joinery Skipton UK"
    },
    {
        "company": "Aspire Kitchen Design",
        "url": "https://aspirekitchendesign.co.uk",
        "email": "info@aspirekitchendesign.co.uk",
        "role": "Bespoke Designer Kitchens Stirling & Perth Scotland UK"
    },
    {
        "company": "Oldbridge Kitchens",
        "url": "https://oldbridgekitchens.com",
        "email": "info@oldbridgekitchens.com",
        "role": "Bespoke Handcrafted Kitchens Meath Ireland"
    },
    {
        "company": "Ornan Kitchens",
        "url": "https://ornanworks.ie",
        "email": "info@ornanworks.ie",
        "role": "Custom Bespoke Kitchens & Cabinetry Navan Meath Ireland"
    },
    {
        "company": "Handcraft Kitchens",
        "url": "https://handcraftkitchens.ie",
        "email": "info@handcraftkitchens.ie",
        "role": "Handmade Bespoke Kitchens County Meath Ireland"
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
    email = c["email"].lower()
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
    from outreach.mailer import verify_mailbox_smtp
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
