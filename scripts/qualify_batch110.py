import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classes.Outreach import Outreach
from outreach.mailer import verify_mailbox_smtp

candidates = [
    {
        "company": "Timbercraft Carpentry",
        "url": "https://timbercraftcarpentryco.co.uk",
        "email": "info@timbercraftcarpentryco.co.uk",
        "role": "Bespoke Kitchens & Joinery Yeovil Somerset UK"
    },
    {
        "company": "Maweswood Kitchens",
        "url": "https://maweswood.co.uk",
        "email": "contact@maweswood.co.uk",
        "role": "Bespoke Kitchens & Custom Cabinetry Leamington Spa UK"
    },
    {
        "company": "Jamie Williams Design",
        "url": "https://jamiewilliamsdesign.co.uk",
        "email": "info@jamiewilliamsdesign.co.uk",
        "role": "Bespoke Kitchens & Furniture Cheltenham Gloucestershire UK"
    },
    {
        "company": "Contour Kitchens",
        "url": "https://contourkitchens.co.uk",
        "email": "design@contourkitchens.co.uk",
        "role": "Bespoke Kitchen Design Cheltenham Gloucestershire UK"
    },
    {
        "company": "North West Fitted Furniture",
        "url": "https://northwestfittedfurniture.co.uk",
        "email": "info@nwfittedfurniture.com",
        "role": "Bespoke Fitted Kitchens & Furniture Altrincham Cheshire UK"
    },
    {
        "company": "Laurence Campbell Kitchens",
        "url": "https://laurencecampbell.co.uk",
        "email": "info@laurencecampbell.co.uk",
        "role": "Bespoke Kitchens & Bedrooms Otley West Yorkshire UK"
    },
    {
        "company": "Hargreaves & Auty",
        "url": "https://hargreavesandauty.co.uk",
        "email": "info@hargreavesandauty.co.uk",
        "role": "Bespoke Fitted Kitchens Otley West Yorkshire UK"
    },
    {
        "company": "Interiors of Ilkley",
        "url": "https://interiorsofilkley.co.uk",
        "email": "design@interiorsofilkley.co.uk",
        "role": "Bespoke Kitchen Design Studio Ilkley West Yorkshire UK"
    },
    {
        "company": "Jeremy Wood Interiors",
        "url": "https://jeremywood.co.uk",
        "email": "info@jeremywood.co.uk",
        "role": "Handmade Bespoke Kitchens Ilkley West Yorkshire UK"
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
    smtp_ok = verify_mailbox_smtp(email, sender_addr="ivanbradic46@gmail.com")
    if not smtp_ok:
        print(f"FAILED SMTP: Mailbox probe failed for {email}")
        continue
    print(f"SMTP OK for {email}")

    qualified.append(c)

print(f"\n==========================================")
print(f"QUALIFIED COUNT: {len(qualified)}")
for q in qualified:
    print(f"- {q['company']} | {q['url']} | {q['email']}")
