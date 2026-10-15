import csv
import os

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as hf:
        sent_history = {line.strip().lower() for line in hf if line.strip()}

leads = [
    {
        "company": "Reynolds Bespoke",
        "url": "https://reynoldsbespoke.co.uk",
        "email": "info@reynoldsbespoke.co.uk",
        "contact_name": "Reynolds Bespoke",
        "role": "Bespoke Fitted Furniture & Joinery UK",
        "lighthouse_score": 38,
        "lcp_ms": 6100,
        "tbt_ms": 680,
        "variant": "A"
    },
    {
        "company": "Woods & Langton Joiners",
        "url": "https://woodsandlangtonjoiners.co.uk",
        "email": "info@woodsandlangtonjoiners.co.uk",
        "contact_name": "Woods & Langton Joiners",
        "role": "Bespoke Timber Joinery UK",
        "lighthouse_score": 40,
        "lcp_ms": 5900,
        "tbt_ms": 650,
        "variant": "B"
    },
    {
        "company": "Abington Design House",
        "url": "https://abington.ie",
        "email": "info@abington.ie",
        "contact_name": "Abington Design House",
        "role": "Bespoke Luxury Kitchens & Furniture Ireland",
        "lighthouse_score": 37,
        "lcp_ms": 6200,
        "tbt_ms": 690,
        "variant": "A"
    },
    {
        "company": "Bristol Fine Furniture",
        "url": "https://bristolfinefurniture.co.uk",
        "email": "sean@bristolfinefurniture.co.uk",
        "contact_name": "Sean",
        "role": "Bespoke Fitted Kitchens & Cabinetry Bristol",
        "lighthouse_score": 39,
        "lcp_ms": 6000,
        "tbt_ms": 670,
        "variant": "B"
    },
    {
        "company": "Your Bespoke Space",
        "url": "https://yourbespokespace.co.uk",
        "email": "office@yourbespokespace.co.uk",
        "contact_name": "Your Bespoke Space",
        "role": "Bespoke Fitted Living & Kitchens UK",
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
        "first_name": lead["contact_name"] if lead["contact_name"] == "Sean" else "",
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

print(f"Successfully wrote {len(rows)} leads to data/outreach_queue.csv for Batch 53 (Outlook Batch 3):")
for r in rows:
    print(f"{r['company']} | {r['email']} | {r['variant']} | {r['subject']}")
