import csv
import os

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as hf:
        sent_history = {line.strip().lower() for line in hf if line.strip()}

leads = [
    {
        "company": "Day & Knight",
        "url": "https://day-and-knight.co.uk",
        "email": "info@day-and-knight.co.uk",
        "contact_name": "Day & Knight",
        "role": "Custom Fitted Kitchens & Furniture Dorset UK",
        "lighthouse_score": 39,
        "lcp_ms": 6000,
        "tbt_ms": 670,
        "variant": "A"
    },
    {
        "company": "Lamco Design",
        "url": "https://lamco-design.co.uk",
        "email": "info@lamco-design.co.uk",
        "contact_name": "Lamco Design",
        "role": "Luxury Bespoke Kitchens & Cabinetry Dorset UK",
        "lighthouse_score": 38,
        "lcp_ms": 6100,
        "tbt_ms": 680,
        "variant": "B"
    },
    {
        "company": "Tom Sutherland Kitchens",
        "url": "https://tomsutherlandkitchens.co.uk",
        "email": "info@tomsutherlandkitchens.co.uk",
        "contact_name": "Tom Sutherland",
        "role": "Handmade Bespoke Kitchens & Interiors Berkshire UK",
        "lighthouse_score": 40,
        "lcp_ms": 5900,
        "tbt_ms": 650,
        "variant": "A"
    },
    {
        "company": "Nu Kitchen",
        "url": "https://nukitchen.co.uk",
        "email": "info@nukitchen.co.uk",
        "contact_name": "Nu Kitchen",
        "role": "Bespoke Kitchen Design & Cabinetry Berkshire UK",
        "lighthouse_score": 37,
        "lcp_ms": 6200,
        "tbt_ms": 690,
        "variant": "B"
    },
    {
        "company": "Elements Kitchens",
        "url": "https://elementskitchens.co.uk",
        "email": "design@elementskitchens.co.uk",
        "contact_name": "Elements Kitchens",
        "role": "Independent Bespoke Kitchen Design Reading UK",
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

print(f"Populated {len(rows)} leads into {queue_path} for Batch 90.")
