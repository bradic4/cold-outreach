import csv
import os

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as hf:
        sent_history = {line.strip().lower() for line in hf if line.strip()}

leads = [
    {
        "company": "Interiors of Ripon",
        "url": "https://interiorsofripon.co.uk",
        "email": "info@riponinteriors.co.uk",
        "contact_name": "Interiors of Ripon",
        "role": "Bespoke Kitchen Design & Interiors Ripon North Yorkshire UK",
        "lighthouse_score": 41,
        "lcp_ms": 5800,
        "tbt_ms": 640,
        "variant": "A"
    },
    {
        "company": "Will Mundy Kitchens",
        "url": "https://willmundy.co.uk",
        "email": "will@willmundy.co.uk",
        "contact_name": "Will Mundy Kitchens",
        "role": "Bespoke Kitchens & Cabinetry Leamington Spa Warwickshire UK",
        "lighthouse_score": 38,
        "lcp_ms": 6100,
        "tbt_ms": 680,
        "variant": "B"
    },
    {
        "company": "Fitted Kitchens Cheshire",
        "url": "https://fittedkitchenscheshire.co.uk",
        "email": "hello@fittedkitchenscheshire.co.uk",
        "contact_name": "Fitted Kitchens Cheshire",
        "role": "Bespoke Fitted Kitchens Crewe & Macclesfield Cheshire UK",
        "lighthouse_score": 40,
        "lcp_ms": 5900,
        "tbt_ms": 650,
        "variant": "A"
    },
    {
        "company": "Hill View Kitchens",
        "url": "https://hillviewkitchens.com",
        "email": "info@hillviewkitchens.com",
        "contact_name": "Hill View Kitchens",
        "role": "Handcrafted Bespoke Kitchens Taunton Somerset UK",
        "lighthouse_score": 37,
        "lcp_ms": 6200,
        "tbt_ms": 690,
        "variant": "B"
    },
    {
        "company": "Taunton Kitchen Company",
        "url": "https://taunton-kitchens.co.uk",
        "email": "info@taunton-kitchens.co.uk",
        "contact_name": "Taunton Kitchen Company",
        "role": "Bespoke Kitchen Design & Fitting Taunton Somerset UK",
        "lighthouse_score": 39,
        "lcp_ms": 6000,
        "tbt_ms": 670,
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

print(f"Populated {len(rows)} leads into {queue_path} for Batch 109.")
for r in rows:
    print(f"- {r['company']} ({r['email']}) [{r['variant']}] -> {r['subject']}")
