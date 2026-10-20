import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classes.Outreach import Outreach
from outreach.mailer import verify_mailbox_smtp

candidates = [
    {
        "company": "Interiors of Ripon",
        "url": "https://interiorsofripon.co.uk",
        "email": "info@riponinteriors.co.uk",
        "role": "Bespoke Kitchen Design & Interiors Ripon North Yorkshire UK"
    },
    {
        "company": "Hue Interiors",
        "url": "https://hue-interiors.co.uk",
        "email": "info@hue-interiors.co.uk",
        "role": "Luxury Bespoke Kitchens Wetherby & Harrogate UK"
    },
    {
        "company": "Bespoke Interiors Harrogate",
        "url": "https://bespokeinteriorsharrogate.co.uk",
        "email": "info@bespokeinteriorsharrogate.co.uk",
        "role": "Handcrafted Bespoke Kitchens Harrogate North Yorkshire UK"
    },
    {
        "company": "Will Mundy Kitchens",
        "url": "https://willmundy.co.uk",
        "email": "will@willmundy.co.uk",
        "role": "Bespoke Kitchens & Cabinetry Leamington Spa Warwickshire UK"
    },
    {
        "company": "Fitted Kitchens Cheshire",
        "url": "https://fittedkitchenscheshire.co.uk",
        "email": "hello@fittedkitchenscheshire.co.uk",
        "role": "Bespoke Fitted Kitchens Crewe & Macclesfield Cheshire UK"
    },
    {
        "company": "Hill View Kitchens",
        "url": "https://hillviewkitchens.com",
        "email": "info@hillviewkitchens.com",
        "role": "Handcrafted Bespoke Kitchens Taunton Somerset UK"
    },
    {
        "company": "Taunton Kitchen Company",
        "url": "https://taunton-kitchens.co.uk",
        "email": "info@taunton-kitchens.co.uk",
        "role": "Bespoke Kitchen Design & Fitting Taunton Somerset UK"
    },
    {
        "company": "Timbercraft Carpentry",
        "url": "https://timbercraftcarpentryco.co.uk",
        "email": "info@timbercraftcarpentryco.co.uk",
        "role": "Bespoke Kitchens & Joinery Yeovil Somerset UK"
    },
    {
        "company": "Dwellings of Sherborne",
        "url": "https://dwellingsofsherborne.co.uk",
        "email": "enquiries@dwellingsofsherborne.co.uk",
        "role": "Bespoke Kitchen Design & Installation Sherborne & Yeovil UK"
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
