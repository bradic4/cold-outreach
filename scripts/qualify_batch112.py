import sys
import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classes.Outreach import Outreach
from outreach.mailer import verify_mailbox_smtp

candidates = [
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
    },
    {
        "company": "Sheerin Bespoke",
        "url": "https://sheerinbespoke.co.uk",
        "email": "info@sheerinbespoke.co.uk",
        "role": "Bespoke Luxury Kitchens & Furniture Knutsford Cheshire UK"
    },
    {
        "company": "Brownlow Furniture",
        "url": "https://brownlowfurniture.co.uk",
        "email": "enquiries@brownlowfurniture.co.uk",
        "role": "Bespoke Handmade Kitchens & Cabinetry Cheshire UK"
    },
    {
        "company": "Jordan Alexander Bespoke",
        "url": "https://jordanalexanderbespoke.co.uk",
        "email": "info@jordanalexanderbespoke.co.uk",
        "role": "Bespoke Kitchen Design Studio Cheshire & Manchester UK"
    },
    {
        "company": "Appleton Kitchens",
        "url": "https://appletonkitchens.co.uk",
        "email": "info@appletonkitchens.co.uk",
        "role": "Bespoke Fitted Kitchens Warrington Cheshire UK"
    },
    {
        "company": "Michael Edwards Bespoke",
        "url": "https://mebespoke.co.uk",
        "email": "enquiries@mebespoke.co.uk",
        "role": "Bespoke Kitchens & Bedrooms Wirral Cheshire UK"
    },
    {
        "company": "Matthew Morris Furniture",
        "url": "https://matthewmorrisfurniture.co.uk",
        "email": "info@matthewmorrisfurniture.co.uk",
        "role": "Handmade Bespoke Kitchens Derby Derbyshire UK"
    },
    {
        "company": "Marston Interiors",
        "url": "https://marstoninteriors.co.uk",
        "email": "info@marstoninteriors.co.uk",
        "role": "Bespoke Kitchens & Living Spaces Hilton Derbyshire UK"
    },
    {
        "company": "Allwood Kitchens",
        "url": "https://allwood-kitchens.co.uk",
        "email": "sales@allwood-kitchens.co.uk",
        "role": "Bespoke Fitted Kitchens Shardlow Derby UK"
    }
]

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as hf:
        sent_history = {line.strip().lower() for line in hf if line.strip()}

print(f"Total sent emails in history: {len(sent_history)}")

outreach = Outreach()
qualified = []

for c in candidates:
    email = c["email"].lower().strip()
    domain = c["url"].split("//")[-1].split("/")[0].replace("www.", "").lower().strip()

    print(f"\n--- Checking {c['company']} ({email}) ---")

    if email in sent_history:
        print(f"FAILED: Email already in history: {email}")
        continue
    if domain in sent_history:
        print(f"FAILED: Domain already in history: {domain}")
        continue

    # 1. HTTP 200
    try:
        r = requests.get(c["url"], timeout=10, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, verify=False)
        if r.status_code >= 400:
            print(f"FAILED HTTP status {r.status_code}")
            continue
        print(f"HTTP 200 OK (final url: {r.url})")
    except Exception as e:
        print(f"FAILED HTTP request: {e}")
        continue

    # 2. DNS MX
    if not outreach.is_valid_mx(email):
        print(f"FAILED MX for {email}")
        continue
    print(f"MX Record OK for {email}")

    # 3. SMTP Mailbox Probe
    smtp_ok = verify_mailbox_smtp(email, sender_addr="ivanbradic46@gmail.com")
    if not smtp_ok:
        print(f"FAILED SMTP probe for {email}")
        continue
    print(f"SMTP OK for {email}")

    qualified.append(c)

print("\n==========================================")
print(f"QUALIFIED COUNT: {len(qualified)}")
for q in qualified:
    print(f"- {q['company']} | {q['url']} | {q['email']}")
