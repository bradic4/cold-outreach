import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classes.Outreach import Outreach
from outreach.mailer import verify_mailbox_smtp

candidates = [
    {
        "company": "Hargreaves & Auty",
        "url": "https://www.hargreavesandauty.co.uk",
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
        "company": "Broadway Kitchens",
        "url": "https://bespokekitchensbybroadway.co.uk",
        "email": "enquiries@kitchensbybroadway.co.uk",
        "role": "Luxury Bespoke Kitchens Sutton Coldfield West Midlands UK"
    },
    {
        "company": "Posh Design",
        "url": "https://poshdesignltd.co.uk",
        "email": "info@poshdesignltd.co.uk",
        "role": "Custom Bespoke Kitchens Sutton Coldfield Birmingham UK"
    },
    {
        "company": "Somax Kitchens",
        "url": "https://somaxkitchens.co.uk",
        "email": "toby@somaxkitchens.co.uk",
        "role": "Bespoke Luxury Kitchens Clitheroe Ribble Valley UK"
    },
    {
        "company": "Status Interiors",
        "url": "https://statusinteriors.co.uk",
        "email": "Info@statusinteriors.co.uk",
        "role": "Bespoke Fitted Kitchens Clitheroe Lancashire UK"
    },
    {
        "company": "Oakwood Kitchens",
        "url": "https://oakwoodkitchens.co.uk",
        "email": "info@oakwoodkitchens.co.uk",
        "role": "Bespoke Handmade Kitchens Huddersfield & Wakefield UK"
    },
    {
        "company": "Highley's Kitchens",
        "url": "https://highleysfks.co.uk",
        "email": "info@highleysfks.co.uk",
        "role": "Bespoke Fitted Kitchens Wakefield West Yorkshire UK"
    },
    {
        "company": "Expressions Kitchens",
        "url": "https://expressionskitchens.co.uk",
        "email": "info@expressionskitchens.co.uk",
        "role": "Bespoke Fitted Kitchens Huddersfield West Yorkshire UK"
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
