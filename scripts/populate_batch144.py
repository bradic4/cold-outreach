import csv
import os

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as hf:
        sent_history = {line.strip().lower() for line in hf if line.strip()}

leads = [
    {
        "company": "Euroform",
        "url": "https://euroform.com.au",
        "email": "reception@euroform.com.au",
        "contact_name": "Euroform",
        "role": "Kitchens, Cabinetry & Architectural Joinery Newcastle Australia",
        "lighthouse_score": 40,
        "lcp_ms": 5900,
        "tbt_ms": 650,
        "variant": "A"
    },
    {
        "company": "Halls Cabinets & Joinery",
        "url": "https://hallscabinetsandjoinery.com.au",
        "email": "chris@hallscabinetsandjoinery.com.au",
        "contact_name": "Halls Cabinets & Joinery",
        "role": "Custom Cabinetry & Joinery Toowoomba Australia",
        "lighthouse_score": 38,
        "lcp_ms": 6200,
        "tbt_ms": 680,
        "variant": "B"
    },
    {
        "company": "Serrata Joinery",
        "url": "https://serratajoinery.com.au",
        "email": "enquiries@serratajoinery.com.au",
        "contact_name": "Serrata Joinery",
        "role": "Architectural Joinery & Custom Cabinetry Sunshine Coast Australia",
        "lighthouse_score": 42,
        "lcp_ms": 5700,
        "tbt_ms": 630,
        "variant": "A"
    },
    {
        "company": "Meredith Kitchens",
        "url": "https://meredithkitchens.com.au",
        "email": "info@meredithkitchens.com.au",
        "contact_name": "Meredith Kitchens",
        "role": "Custom Kitchens & Cabinet Makers Sunshine Coast Australia",
        "lighthouse_score": 39,
        "lcp_ms": 6000,
        "tbt_ms": 670,
        "variant": "B"
    },
    {
        "company": "Comsense Kitchen Cabinets",
        "url": "https://comsensekitchencabinets.com",
        "email": "info@comsenseholdings.com",
        "contact_name": "Comsense Kitchen Cabinets",
        "role": "Custom Kitchen Cabinets & Renovation Nanaimo Canada",
        "lighthouse_score": 41,
        "lcp_ms": 5800,
        "tbt_ms": 640,
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

print(f"Populated {len(rows)} leads into {queue_path} for Batch 144.")
for r in rows:
    print(f"- {r['company']} ({r['email']}) [{r['variant']}] -> {r['subject']}")
