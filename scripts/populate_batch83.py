import csv
import os

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as hf:
        sent_history = {line.strip().lower() for line in hf if line.strip()}

leads = [
    {
        "company": "Woodwise Kitchens",
        "url": "https://woodwisekitchens.com",
        "email": "info@woodwisekitchens.com",
        "contact_name": "Woodwise Kitchens",
        "role": "Individually Designed Handmade Bespoke Kitchens & Cabinetry Oxfordshire UK",
        "lighthouse_score": 39,
        "lcp_ms": 6100,
        "tbt_ms": 680,
        "variant": "A"
    },
    {
        "company": "Interact Interiors",
        "url": "https://interactinteriors.co.uk",
        "email": "info@interactinteriors.co.uk",
        "contact_name": "Interact Interiors",
        "role": "Bespoke Architectural Joinery & Interior Fit-Outs Scotland UK",
        "lighthouse_score": 41,
        "lcp_ms": 5800,
        "tbt_ms": 640,
        "variant": "B"
    },
    {
        "company": "GS Bespoke Joinery",
        "url": "https://gsbj.co.uk",
        "email": "info@gsbj.co.uk",
        "contact_name": "GS Bespoke Joinery",
        "role": "Master Craftsmen Bespoke Furniture & Architectural Joinery Scotland UK",
        "lighthouse_score": 38,
        "lcp_ms": 6200,
        "tbt_ms": 690,
        "variant": "A"
    },
    {
        "company": "Berkshire Kitchen Studio",
        "url": "https://berkshirekitchenstudio.co.uk",
        "email": "info@berkshirekitchenstudio.co.uk",
        "contact_name": "Berkshire Kitchen Studio",
        "role": "Custom Kitchen Design & Handcrafted Installation Berkshire UK",
        "lighthouse_score": 40,
        "lcp_ms": 5900,
        "tbt_ms": 660,
        "variant": "B"
    },
    {
        "company": "Bristol & Bath Kitchens",
        "url": "https://bristolandbathkitchens.co.uk",
        "email": "info@bristolandbathkitchens.co.uk",
        "contact_name": "Bristol & Bath Kitchens",
        "role": "Luxury Bespoke Kitchens & Living Spaces Bristol & Bath UK",
        "lighthouse_score": 37,
        "lcp_ms": 6300,
        "tbt_ms": 700,
        "variant": "A"
    }
]

body_template = """Hi,

I had a look at your company's website and noticed a few things that could be improved, especially when potential clients open it on their mobile phone.

For bespoke kitchen and joinery companies, the website is usually the first point of contact with a future client. That's why it's important that it quickly showcases your work and services and makes it effortless for visitors to get in touch.

I specialize in website optimization and have a few specific ideas on how you could improve the mobile experience and increase enquiries.

I can send over a short free breakdown with the 3 things I'd change first.

Would you like to take a look at it?

Best,
Ivan Bradić
ivanbradic.vercel.app"""

rows = []
for lead in leads:
    em = lead["email"].strip().lower()
    dom = lead["url"].split("//")[-1].split("/")[0].replace("www.", "").lower()
    if em in sent_history:
        raise ValueError(f"Email {em} already in history!")
    if dom in sent_history:
        raise ValueError(f"Domain {dom} already in history!")

    subj = "Quick suggestion for your website" if lead["variant"] == "A" else f"Quick question about {lead['company']}'s website"

    rows.append({
        "company": lead["company"],
        "url": lead["url"],
        "email": lead["email"],
        "contact_name": lead["contact_name"],
        "first_name": "",
        "role": lead["role"],
        "lighthouse_score": lead["lighthouse_score"],
        "lcp_ms": lead["lcp_ms"],
        "tbt_ms": lead["tbt_ms"],
        "variant": lead["variant"],
        "subject": subj,
        "message": body_template,
        "status": "ready"
    })

fieldnames = ["company", "url", "email", "contact_name", "first_name", "role", "lighthouse_score", "lcp_ms", "tbt_ms", "variant", "subject", "message", "status"]
with open("data/outreach_queue.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Successfully wrote {len(rows)} leads to data/outreach_queue.csv for Batch 83:")
for r in rows:
    print(f"{r['company']} | {r['email']} | {r['variant']} | {r['subject']}")
