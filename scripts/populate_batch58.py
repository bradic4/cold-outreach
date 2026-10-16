import csv
import os

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as hf:
        sent_history = {line.strip().lower() for line in hf if line.strip()}

leads = [
    {
        "company": "Cotswold Oak Joinery",
        "url": "https://cotswoldoakjoinery.co.uk",
        "email": "info@cotswoldoakjoinery.co.uk",
        "contact_name": "Cotswold Oak Joinery",
        "role": "Bespoke Joinery Pantries & Handmade Kitchens Cotswolds",
        "lighthouse_score": 38,
        "lcp_ms": 6100,
        "tbt_ms": 680,
        "variant": "A"
    },
    {
        "company": "Yorkshire Kitchen Design",
        "url": "https://yorkshirekitchendesign.co.uk",
        "email": "info@yorkshirekitchendesign.co.uk",
        "contact_name": "Yorkshire Kitchen Design",
        "role": "Bespoke Modern & Shaker Fitted Kitchens York",
        "lighthouse_score": 40,
        "lcp_ms": 5900,
        "tbt_ms": 650,
        "variant": "B"
    },
    {
        "company": "Concannon Fitted Kitchens",
        "url": "https://concannonkitchens.ie",
        "email": "info@concannonkitchens.ie",
        "contact_name": "Concannon Fitted Kitchens",
        "role": "Custom Manufactured Fitted Kitchens & Cabinetry Westmeath",
        "lighthouse_score": 37,
        "lcp_ms": 6200,
        "tbt_ms": 690,
        "variant": "A"
    },
    {
        "company": "Jeremy Wood Interiors",
        "url": "https://jeremywood.co.uk",
        "email": "info@jeremywood.co.uk",
        "contact_name": "Jeremy Wood Interiors",
        "role": "Handmade Bespoke Kitchens & Interior Cabinetry Yorkshire",
        "lighthouse_score": 39,
        "lcp_ms": 6000,
        "tbt_ms": 670,
        "variant": "B"
    },
    {
        "company": "Creative Wood",
        "url": "https://creativewood.ie",
        "email": "info@creativewood.ie",
        "contact_name": "Creative Wood",
        "role": "Handmade Luxury Bespoke Kitchens & Interiors Mayo",
        "lighthouse_score": 36,
        "lcp_ms": 6400,
        "tbt_ms": 710,
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

print(f"Successfully wrote {len(rows)} leads to data/outreach_queue.csv for Batch 58 (Outlook Batch 8):")
for r in rows:
    print(f"{r['company']} | {r['email']} | {r['variant']} | {r['subject']}")
