import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classes.Outreach import Outreach
from outreach.mailer import verify_mailbox_smtp

candidates = [
    {
        "company": "Kitchen Lifestyles",
        "url": "https://www.kitchenlifestyles.co.uk",
        "email": "hello@kitchenlifestyles.co.uk",
        "role": "Bespoke Fitted Kitchens Hampshire UK"
    },
    {
        "company": "Kitchens of Winchester",
        "url": "https://www.kitchensofwinchester.co.uk",
        "email": "ben@k-o-w.co.uk",
        "role": "Bespoke Kitchen Design Winchester Hampshire UK"
    },
    {
        "company": "Kraus Kitchens",
        "url": "https://krauskitchens.co.uk",
        "email": "info@krauskitchens.co.uk",
        "role": "Luxury Bespoke Kitchens Sevenoaks & Tunbridge Wells UK"
    },
    {
        "company": "Cove Kitchens",
        "url": "https://covekitchens.co.uk",
        "email": "hello@covekitchens.co.uk",
        "role": "Bespoke Kitchens & Living Spaces Tunbridge Wells Kent UK"
    },
    {
        "company": "Guildford Kitchens",
        "url": "https://guildfordkitchens.co.uk",
        "email": "office@guildfordkitchens.co.uk",
        "role": "Bespoke Fitted Kitchens Guildford Surrey UK"
    },
    {
        "company": "Lucas Grant Kitchens",
        "url": "https://lucasgrant.co.uk",
        "email": "hello@lucasgrant.co.uk",
        "role": "Handcrafted Bespoke Kitchens Farnham Surrey UK"
    },
    {
        "company": "Park House Kitchens",
        "url": "https://phk.co.uk",
        "email": "info@phk.co.uk",
        "role": "Bespoke Kitchen Design Dorking & Guildford Surrey UK"
    },
    {
        "company": "Kelly Interiors",
        "url": "https://kellyinteriors.ie",
        "email": "design@kellyinteriors.ie",
        "role": "Bespoke Fitted Kitchens Naas Kildare Ireland"
    },
    {
        "company": "Clarke Kitchens",
        "url": "https://clarkekitchens.ie",
        "email": "sian@clarkekitchens.ie",
        "role": "Handcrafted Bespoke Kitchens Naas Kildare Ireland"
    },
    {
        "company": "The Kitchen Company",
        "url": "https://kitchencompany.ie",
        "email": "info@kitchencompany.ie",
        "role": "Bespoke Kitchens & Living Spaces Kildare Ireland"
    },
    {
        "company": "Leo Reilly Woodcraft",
        "url": "https://leoreilly.com",
        "email": "info@leoreilly.com",
        "role": "Bespoke Architectural Joinery & Kitchens Naas Ireland"
    },
    {
        "company": "Kerins Interiors",
        "url": "https://kerinsinteriors.ie",
        "email": "info@kerinsinteriors.ie",
        "role": "Custom Bespoke Kitchens Kilkenny & Kildare Ireland"
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
