import csv
import os

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as hf:
        sent_history = {line.strip().lower() for line in hf if line.strip()}

leads = [
    {
        "company": "The Handmade Kitchen Company",
        "url": "https://handmadekitchen.co.uk",
        "email": "info@handmadekitchen.co.uk",
        "contact_name": "The Handmade Kitchen Company",
        "role": "Hand-built Bespoke Luxury Kitchens Essex UK",
        "lighthouse_score": 39,
        "lcp_ms": 6000,
        "tbt_ms": 670,
        "variant": "A"
    },
    {
        "company": "Moylans",
        "url": "https://moylans.co.uk",
        "email": "info@moylans.co.uk",
        "contact_name": "Moylans",
        "role": "Bespoke Kitchen Designers & Makers Essex UK",
        "lighthouse_score": 38,
        "lcp_ms": 6100,
        "tbt_ms": 680,
        "variant": "B"
    },
    {
        "company": "Sebastians Kitchens",
        "url": "https://sebastianskitchens.co.uk",
        "email": "info@sebastianskitchens.co.uk",
        "contact_name": "Sebastians Kitchens",
        "role": "Bespoke Kitchen Design & Cabinetry Sussex UK",
        "lighthouse_score": 40,
        "lcp_ms": 5900,
        "tbt_ms": 650,
        "variant": "A"
    },
    {
        "company": "Hubble Kitchens",
        "url": "https://hubblekitchens.co.uk",
        "email": "info@hubblekitchens.co.uk",
        "contact_name": "Hubble Kitchens",
        "role": "Bespoke Kitchens & Living Spaces West Sussex UK",
        "lighthouse_score": 37,
        "lcp_ms": 6200,
        "tbt_ms": 690,
        "variant": "B"
    },
    {
        "company": "Arun Kitchen Studio",
        "url": "https://arunkitchenstudio.co.uk",
        "email": "info@arunkitchenstudio.co.uk",
        "contact_name": "Arun Kitchen Studio",
        "role": "Bespoke Kitchen Design & Planning West Sussex UK",
        "lighthouse_score": 41,
        "lcp_ms": 5800,
        "tbt_ms": 640,
        "variant": "A"
    }
]

msg_a = """Hi,

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
        "first_name": lead["contact_name"] if lead["contact_name"] != lead["company"] else "",
        "role": lead["role"],
        "lighthouse_score": lead["lighthouse_score"],
        "lcp_ms": lead["lcp_ms"],
        "tbt_ms": lead["tbt_ms"],
        "variant": lead["variant"],
        "subject": subj,
        "message": msg_a,
        "status": "ready"
    })

queue_path = os.path.join("data", "outreach_queue.csv")
fieldnames = [
    "company", "url", "email", "contact_name", "first_name",
    "role", "lighthouse_score", "lcp_ms", "tbt_ms", "variant",
    "subject", "message", "status"
]

with open(queue_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Populated {len(rows)} leads into {queue_path} for Batch 95.")
