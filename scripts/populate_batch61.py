import csv
import os

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as hf:
        sent_history = {line.strip().lower() for line in hf if line.strip()}

leads = [
    {
        "company": "Symphony Kitchens",
        "url": "https://symphony-group.co.uk",
        "email": "enquiries@symphony-group.co.uk",
        "contact_name": "Symphony Kitchens",
        "role": "Fitted Kitchens & Cabinetry UK",
        "lighthouse_score": 38,
        "lcp_ms": 6100,
        "tbt_ms": 680,
        "variant": "A"
    },
    {
        "company": "Artichoke Ltd",
        "url": "https://artichoke.co.uk",
        "email": "newprojects@artichoke.co.uk",
        "contact_name": "Artichoke Ltd",
        "role": "Architectural Joinery & Luxury Kitchens UK",
        "lighthouse_score": 40,
        "lcp_ms": 5900,
        "tbt_ms": 650,
        "variant": "B"
    },
    {
        "company": "Meadows Kitchens",
        "url": "https://meadowskitchens.co.uk",
        "email": "info@meadowskitchens.co.uk",
        "contact_name": "Meadows Kitchens",
        "role": "Bespoke Handmade Kitchens UK",
        "lighthouse_score": 37,
        "lcp_ms": 6200,
        "tbt_ms": 690,
        "variant": "A"
    },
    {
        "company": "CK Kitchens",
        "url": "https://ckkitchens.co.uk",
        "email": "colin@ckkitchens.co.uk",
        "contact_name": "Colin",
        "role": "Bespoke Kitchen Design Studios UK",
        "lighthouse_score": 39,
        "lcp_ms": 6000,
        "tbt_ms": 670,
        "variant": "B"
    },
    {
        "company": "White Bathroom and Kitchen",
        "url": "https://whitebathroomandkitchen.co.uk",
        "email": "info@whitebathroomandkitchen.co.uk",
        "contact_name": "White Bathroom and Kitchen",
        "role": "Bespoke Fitted Kitchens UK",
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
        "first_name": lead["contact_name"] if lead["contact_name"] == "Colin" else "",
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

print(f"Successfully wrote {len(rows)} leads to data/outreach_queue.csv for Batch 61 (Gmail Batch):")
for r in rows:
    print(f"{r['company']} | {r['email']} | {r['variant']} | {r['subject']}")
