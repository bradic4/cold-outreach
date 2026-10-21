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
        "company": "Shaker & May",
        "url": "https://shakerandmay.co.uk",
        "email": "info@shakerandmay.co.uk",
        "role": "Handmade Bespoke Kitchens Bath & Somerset UK"
    },
    {
        "company": "Yealm Kitchens",
        "url": "https://yealmkitchens.co.uk",
        "email": "info@yealmkitchens.co.uk",
        "role": "Bespoke Wood Kitchens & Fitted Furniture Plymouth Devon UK"
    },
    {
        "company": "Hayman Joinery",
        "url": "https://haymanjoinery.co.uk",
        "email": "info@haymanjoinery.co.uk",
        "role": "Custom Architectural Joinery & Bespoke Kitchens Plymouth UK"
    },
    {
        "company": "TRS Bespoke Interiors",
        "url": "https://trsbespokeinteriors.co.uk",
        "email": "info@trsbespokeinteriors.co.uk",
        "role": "Bespoke Kitchen Design & Cabinetry Exeter Devon UK"
    },
    {
        "company": "Taunton Kitchens",
        "url": "https://tauntonkitchens.co.uk",
        "email": "info@tauntonkitchens.co.uk",
        "role": "Bespoke Fitted Kitchens Taunton Somerset UK"
    },
    {
        "company": "Taunton Carpentry",
        "url": "https://tauntoncarpentry.co.uk",
        "email": "info@tauntoncarpentry.co.uk",
        "role": "Bespoke Kitchens & Custom Carpentry Taunton Somerset UK"
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
    smtp_ok = verify_mailbox_smtp(email, sender_addr="ivanbradic.biz@gmail.com")
    if not smtp_ok:
        print(f"FAILED SMTP probe for {email}")
        continue
    print(f"SMTP OK for {email}")

    qualified.append(c)

print("\n==========================================")
print(f"QUALIFIED COUNT: {len(qualified)}")
for q in qualified:
    print(f"- {q['company']} | {q['url']} | {q['email']}")
