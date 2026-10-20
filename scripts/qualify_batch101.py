import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classes.Outreach import Outreach
from outreach.mailer import verify_mailbox_smtp

candidates = [
    {
        "company": "Bella Kitchens",
        "url": "https://www.bella-kitchensdorset.co.uk",
        "email": "info@bella-kitchens.co.uk",
        "role": "Bespoke Fitted Kitchens Poundbury Dorchester UK"
    },
    {
        "company": "Solutions Kitchens",
        "url": "https://www.solutions-kitchensandbathrooms.co.uk",
        "email": "sales@solutions-kitchensandbathrooms.co.uk",
        "role": "Tailored Kitchens & Living Spaces Weymouth Dorset UK"
    },
    {
        "company": "Dorset Kitchens",
        "url": "https://dorsetkitchens.co.uk",
        "email": "sales@dorsetkitchens.co.uk",
        "role": "Handmade Bespoke Kitchens & Cabinetry Dorset UK"
    },
    {
        "company": "Bath Bespoke",
        "url": "https://bathbespoke.co.uk",
        "email": "enquiries@bathbespoke.co.uk",
        "role": "Luxury Handcrafted Kitchens & Joinery Bath UK"
    },
    {
        "company": "Brunswick Bespoke",
        "url": "https://brunswickbespoke.co.uk",
        "email": "info@brunswickbespoke.co.uk",
        "role": "Bespoke Kitchen Design & Cabinetry Somerset UK"
    },
    {
        "company": "Somerset Kitchen Design",
        "url": "https://somersetkitchendesignstudio.co.uk",
        "email": "info@somersetkitchendesign.co.uk",
        "role": "Bespoke Kitchen Design Studio Somerset UK"
    },
    {
        "company": "Monkeywood Kitchens",
        "url": "https://monkeywood.co.uk",
        "email": "design@monkeywood.co.uk",
        "role": "Handmade Bespoke Kitchens Banbury Oxfordshire UK"
    },
    {
        "company": "HeartWood Furniture",
        "url": "https://heartwoodfurniture.co.uk",
        "email": "sales@heartwoodfurniture.co.uk",
        "role": "Handmade Solid Wood Kitchens Witney Oxfordshire UK"
    },
    {
        "company": "Claremont Kitchens",
        "url": "https://claremontkitchens.co.uk",
        "email": "sales@claremontkitchens.co.uk",
        "role": "Bespoke Kitchens & Living Spaces Midhurst Sussex UK"
    },
    {
        "company": "Kitchen Lifestyles",
        "url": "https://kitchenlifestyles.co.uk",
        "email": "hello@kitchenlifestyles.co.uk",
        "role": "Bespoke Fitted Kitchens Hampshire UK"
    },
    {
        "company": "Kitchens of Winchester",
        "url": "https://kitchensofwinchester.co.uk",
        "email": "ben@k-o-w.co.uk",
        "role": "Bespoke Kitchen Design Winchester Hampshire UK"
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
