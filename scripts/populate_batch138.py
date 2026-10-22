import csv
import os

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as hf:
        sent_history = {line.strip().lower() for line in hf if line.strip()}

leads = [
    {
        "company": "Coastal Accents",
        "url": "https://coastalaccents.ca",
        "email": "info@coastalaccents.ca",
        "contact_name": "Coastal Accents",
        "role": "Custom Cabinetry & Millwork Victoria Canada",
        "lighthouse_score": 42,
        "lcp_ms": 5700,
        "tbt_ms": 630,
        "variant": "B"
    },
    {
        "company": "Sensible Kitchens",
        "url": "https://sensiblekitchens.ca",
        "email": "info@sensiblekitchens.ca",
        "contact_name": "Sensible Kitchens",
        "role": "Custom Kitchens & Cabinet Renovations Victoria Canada",
        "lighthouse_score": 39,
        "lcp_ms": 6000,
        "tbt_ms": 670,
        "variant": "A"
    },
    {
        "company": "Lighthouse Kitchens",
        "url": "https://lighthousekitchens.ca",
        "email": "info@lighthousekitchens.ca",
        "contact_name": "Lighthouse Kitchens",
        "role": "Bespoke Cabinetry & Custom Kitchens Victoria Canada",
        "lighthouse_score": 40,
        "lcp_ms": 5900,
        "tbt_ms": 650,
        "variant": "B"
    },
    {
        "company": "Urbana Kitchens",
        "url": "https://urbanakitchens.ca",
        "email": "info@urbanakitchens.ca",
        "contact_name": "Urbana Kitchens",
        "role": "Custom Kitchen Design & Cabinet Lines Victoria Canada",
        "lighthouse_score": 38,
        "lcp_ms": 6100,
        "tbt_ms": 680,
        "variant": "A"
    },
    {
        "company": "Provincial Cabinets",
        "url": "https://provincialcabinets.com",
        "email": "sales@provincialcabinets.com",
        "contact_name": "Provincial Cabinets",
        "role": "Kitchen Cabinetry & 3D Design Victoria Canada",
        "lighthouse_score": 41,
        "lcp_ms": 5800,
        "tbt_ms": 640,
        "variant": "B"
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

print(f"Populated {len(rows)} leads into {queue_path} for Batch 138.")
for r in rows:
    print(f"- {r['company']} ({r['email']}) [{r['variant']}] -> {r['subject']}")
