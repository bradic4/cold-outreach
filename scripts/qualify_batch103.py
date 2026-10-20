import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classes.Outreach import Outreach
from outreach.mailer import verify_mailbox_smtp

candidates = [
    {
        "company": "Leo Reilly Woodcraft",
        "url": "https://leoreilly.com",
        "email": "info@leoreilly.com",
        "role": "Bespoke Architectural Joinery & Kitchens Naas Ireland"
    },
    {
        "company": "Oxfordshire & Buckinghamshire Kitchens",
        "url": "https://oxfordshirebuckinghamshirekitchens.co.uk",
        "email": "info@oxfordshirebuckinghamshirekitchens.co.uk",
        "role": "Bespoke Fitted Kitchens Gerrards Cross Buckinghamshire UK"
    },
    {
        "company": "Fortress Kitchens",
        "url": "https://fortresskitchens.ie",
        "email": "info@fortresskitchens.ie",
        "role": "Handcrafted Bespoke Kitchens Cork Ireland"
    },
    {
        "company": "Kube Interiors",
        "url": "https://www.kubeinteriors.com",
        "email": "info@kubeinteriors.com",
        "role": "Designer Bespoke Kitchens & Living Cork Ireland"
    },
    {
        "company": "Stylcraft Kitchens",
        "url": "https://stylecraft.ie",
        "email": "info@stylecraft.ie",
        "role": "Bespoke Kitchens & Custom Cabinetry Ballincollig Cork Ireland"
    },
    {
        "company": "Connaught Kitchens",
        "url": "https://connaughtkitchens.com",
        "email": "stephen@connaughtkitchens.com",
        "role": "Bespoke Kitchen Design & Cabinetry Tuam Galway Ireland"
    },
    {
        "company": "Diskin Kitchens",
        "url": "https://diskinkitchens.com",
        "email": "enquiries@diskinkitchens.com",
        "role": "Handmade Bespoke Kitchens Milltown Galway Ireland"
    },
    {
        "company": "Finlay Kitchens",
        "url": "https://finlaykitchens.com",
        "email": "info@finlaykitchens.com",
        "role": "Bespoke Fitted Kitchens Galway Ireland"
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
