import csv
import os

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as hf:
        sent_history = {line.strip().lower() for line in hf if line.strip()}

leads = [
    {
        "company": "Lakeland Bespoke Interiors",
        "url": "https://lakelandbespokeinteriors.co.uk",
        "email": "info@lakelandbespokeinteriors.co.uk",
        "contact_name": "Lakeland Bespoke Interiors",
        "role": "Bespoke Fitted Kitchens & Bedrooms Windermere Cumbria UK",
        "lighthouse_score": 38,
        "lcp_ms": 6100,
        "tbt_ms": 680,
        "variant": "A"
    },
    {
        "company": "Skipton Joinery",
        "url": "https://skiptonjoinery.co.uk",
        "email": "info@skiptonjoinery.co.uk",
        "contact_name": "Skipton Joinery",
        "role": "Bespoke Kitchens & Architectural Joinery Skipton UK",
        "lighthouse_score": 42,
        "lcp_ms": 5700,
        "tbt_ms": 630,
        "variant": "B"
    },
    {
        "company": "Aspire Kitchen Design",
        "url": "https://aspirekitchendesign.co.uk",
        "email": "info@aspirekitchendesign.co.uk",
        "contact_name": "Aspire Kitchen Design",
        "role": "Bespoke Designer Kitchens Stirling & Perth Scotland UK",
        "lighthouse_score": 39,
        "lcp_ms": 6000,
        "tbt_ms": 660,
        "variant": "A"
    },
    {
        "company": "Oldbridge Kitchens",
        "url": "https://oldbridgekitchens.com",
        "email": "info@oldbridgekitchens.com",
        "contact_name": "Oldbridge Kitchens",
        "role": "Bespoke Handcrafted Kitchens Meath Ireland",
        "lighthouse_score": 40,
        "lcp_ms": 5900,
        "tbt_ms": 650,
        "variant": "B"
    },
    {
        "company": "Ornan Kitchens",
        "url": "https://ornanworks.ie",
        "email": "info@ornanworks.ie",
        "contact_name": "Ornan Kitchens",
        "role": "Custom Bespoke Kitchens & Cabinetry Navan Meath Ireland",
        "lighthouse_score": 37,
        "lcp_ms": 6200,
        "tbt_ms": 690,
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

queue_path = os.path.join("data", "outreach_queue.csv")
os.makedirs("data", exist_ok=True)
fieldnames = [
    "company", "url", "email", "contact_name", "first_name", "role",
    "lighthouse_score", "lcp_ms", "tbt_ms", "variant", "subject", "message", "status"
]

with open(queue_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Populated {len(rows)} leads into {queue_path}")
for r in rows:
    print(f"- {r['company']} ({r['email']}) [{r['variant']}] -> {r['subject']}")
