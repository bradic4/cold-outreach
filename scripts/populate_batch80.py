import csv
import os

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as hf:
        sent_history = {line.strip().lower() for line in hf if line.strip()}

leads = [
    {
        "company": "Evans Bespoke Kitchens",
        "url": "https://evansbespoke.co.uk",
        "email": "info@evansbespoke.co.uk",
        "contact_name": "Evans Bespoke Kitchens",
        "role": "Bespoke Kitchen Design & Handcrafted Living Hampshire UK",
        "lighthouse_score": 38,
        "lcp_ms": 6100,
        "tbt_ms": 680,
        "variant": "A"
    },
    {
        "company": "Built In Furniture",
        "url": "https://builtin-furniture.co.uk",
        "email": "info@builtin-furniture.co.uk",
        "contact_name": "Built In Furniture",
        "role": "Handcrafted Bespoke Kitchens & Fitted Furniture UK",
        "lighthouse_score": 40,
        "lcp_ms": 5900,
        "tbt_ms": 650,
        "variant": "B"
    },
    {
        "company": "Lund & Law",
        "url": "https://lundandlaw.co.uk",
        "email": "enquiries@lundandlaw.co.uk",
        "contact_name": "Lund & Law",
        "role": "Luxury Handcrafted Bespoke Kitchens & Cabinetry North Yorkshire UK",
        "lighthouse_score": 39,
        "lcp_ms": 6000,
        "tbt_ms": 670,
        "variant": "A"
    },
    {
        "company": "Rencraft",
        "url": "https://rencraft.co.uk",
        "email": "info@rencraft.co.uk",
        "contact_name": "Rencraft",
        "role": "Award-Winning Handmade Kitchens & Cabinet Makers Kent UK",
        "lighthouse_score": 41,
        "lcp_ms": 5800,
        "tbt_ms": 640,
        "variant": "B"
    },
    {
        "company": "London Bespoke Kitchen & Joinery",
        "url": "https://londonbespokekitchenjoinery.co.uk",
        "email": "info@londonbespokekitchenjoinery.co.uk",
        "contact_name": "London Bespoke Kitchen & Joinery",
        "role": "Luxury Bespoke Kitchens & Architectural Joinery London UK",
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

print(f"Successfully wrote {len(rows)} leads to data/outreach_queue.csv for Batch 80:")
for r in rows:
    print(f"{r['company']} | {r['email']} | {r['variant']} | {r['subject']}")
