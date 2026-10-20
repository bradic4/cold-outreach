import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classes.Outreach import Outreach
from outreach.mailer import verify_mailbox_smtp

candidates = [
    {
        "company": "Ravelglen Products",
        "url": "https://ravelglen.co.uk",
        "email": "info@ravelglen.co.uk",
        "role": "Bespoke Fitted Kitchens & Furniture Ballymena Northern Ireland"
    },
    {
        "company": "Nick Archibold",
        "url": "https://nickarchibold.com",
        "email": "nick@nickarchibold.com",
        "role": "Bespoke Handmade Kitchens & Cabinetry Wiltshire UK"
    },
    {
        "company": "Olive Madison",
        "url": "https://olivemadison.co.uk",
        "email": "info@olivemadison.co.uk",
        "role": "Bespoke Kitchen Design Salisbury Wiltshire UK"
    },
    {
        "company": "Your Bespoke Space",
        "url": "https://yourbespokespace.co.uk",
        "email": "office@yourbespokespace.co.uk",
        "role": "Bespoke Kitchens & Living Spaces Preston Lancashire UK"
    },
    {
        "company": "Ulmo",
        "url": "https://ulmo.co.uk",
        "email": "info@ulmo.co.uk",
        "role": "Contemporary Bespoke Kitchens Lancashire UK"
    },
    {
        "company": "Matthew Marsden Furniture",
        "url": "https://mmfurniture.co.uk",
        "email": "info@mmfurniture.co.uk",
        "role": "Handmade Bespoke Kitchens Ribble Valley Lancashire UK"
    },
    {
        "company": "Prestons Kitchens",
        "url": "https://prestonskitchens.co.uk",
        "email": "info@prestonskitchens.co.uk",
        "role": "Bespoke Fitted Kitchens Preston Lancashire UK"
    },
    {
        "company": "Kitchen Culture",
        "url": "https://kitchenculturecambridgeshire.co.uk",
        "email": "info@kitchenculturecambridgeshire.co.uk",
        "role": "Bespoke Kitchen Design Cambridgeshire & Bedfordshire UK"
    },
    {
        "company": "Woodstyle Joinery",
        "url": "https://woodstylejoinery.co.uk",
        "email": "joiners@woodstylejoinery.co.uk",
        "role": "Handcrafted Bespoke Kitchens Carlisle Cumbria UK"
    },
    {
        "company": "Cumbria Kitchens",
        "url": "https://cumbriakitchens.co.uk",
        "email": "sales@cumbriakitchens.co.uk",
        "role": "Bespoke Fitted Kitchens Carlisle Penrith Cumbria UK"
    },
    {
        "company": "The Bespoke Home",
        "url": "https://thebespokehome.co.uk",
        "email": "enquiries@thebespokehome.co.uk",
        "role": "Bespoke Handcrafted Furniture & Kitchens Penrith Cumbria UK"
    },
    {
        "company": "Made to Bespoke Joinery",
        "url": "https://madetobespokejoinery.co.uk",
        "email": "info@madetobespokejoinery.co.uk",
        "role": "Bespoke Kitchens & Architectural Joinery Darlington Durham UK"
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
