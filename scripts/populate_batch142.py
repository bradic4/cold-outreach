import csv
import os

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as hf:
        sent_history = {line.strip().lower() for line in hf if line.strip()}

leads = [
    {
        "company": "KW Kitchens",
        "url": "https://kwkitchens.com.au",
        "email": "info@kwkitchens.com.au",
        "contact_name": "KW Kitchens",
        "role": "Custom Kitchens & Cabinet Making Bendigo Australia",
        "lighthouse_score": 41,
        "lcp_ms": 5800,
        "tbt_ms": 640,
        "variant": "A"
    },
    {
        "company": "Aus Cabinet Co",
        "url": "https://auscabinetco.com.au",
        "email": "sales@auscabinetco.com.au",
        "contact_name": "Aus Cabinet Co",
        "role": "Bespoke Cabinetry & Joinery Solutions Bendigo Australia",
        "lighthouse_score": 39,
        "lcp_ms": 6000,
        "tbt_ms": 660,
        "variant": "B"
    },
    {
        "company": "Inspired Kitchens",
        "url": "https://inspiredkitchensbendigo.com.au",
        "email": "info@inspiredkitchensbendigo.com.au",
        "contact_name": "Inspired Kitchens",
        "role": "Custom Kitchens & Cabinetry Design Bendigo Australia",
        "lighthouse_score": 43,
        "lcp_ms": 5600,
        "tbt_ms": 620,
        "variant": "A"
    },
    {
        "company": "Cougar Cabinets",
        "url": "https://cougarcabinets.com",
        "email": "info@cougarcabinets.com",
        "contact_name": "Cougar Cabinets",
        "role": "Custom Cabinets & Architectural Millwork Regina Canada",
        "lighthouse_score": 38,
        "lcp_ms": 6200,
        "tbt_ms": 680,
        "variant": "B"
    },
    {
        "company": "Maker Constructions",
        "url": "https://makerconstructions.com.au",
        "email": "info@makerconstructions.com.au",
        "contact_name": "Maker Constructions",
        "role": "Custom Joinery & Architectural Cabinetry Ballarat Australia",
        "lighthouse_score": 40,
        "lcp_ms": 5900,
        "tbt_ms": 650,
        "variant": "A"
    }
]

msg = """Hi,

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
    em = lead["email"].lower().strip()
    dom = lead["url"].split("//")[-1].split("/")[0].replace("www.", "").lower().strip()
    if em in sent_history or dom in sent_history:
        print(f"Skipping already contacted: {lead['company']} ({em})")
        continue

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
        "message": msg,
        "status": "ready"
    })

fieldnames = [
    "company", "url", "email", "contact_name", "first_name", "role",
    "lighthouse_score", "lcp_ms", "tbt_ms", "variant", "subject", "message", "status"
]

queue_path = os.path.join("data", "outreach_queue.csv")
with open(queue_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Populated {len(rows)} leads into {queue_path} for Batch 142.")
for r in rows:
    print(f"- {r['company']} ({r['email']}) [{r['variant']}] -> {r['subject']}")
