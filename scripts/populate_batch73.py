import csv
import os

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as hf:
        sent_history = {line.strip().lower() for line in hf if line.strip()}

leads = [
    {
        "company": "R E Woods Cabinetmakers",
        "url": "https://bespokekitchensnorfolk.co.uk",
        "email": "contact@rewoods-cabinetmakers.com",
        "contact_name": "R E Woods Cabinetmakers",
        "role": "Bespoke Handcrafted Kitchens & Cabinetmakers Norfolk UK",
        "lighthouse_score": 38,
        "lcp_ms": 6100,
        "tbt_ms": 670,
        "variant": "A"
    },
    {
        "company": "Wentwood Kitchens",
        "url": "https://wentwoodkitchens.co.uk",
        "email": "hello@wentwoodgroup.com",
        "contact_name": "Wentwood Kitchens",
        "role": "Handmade Kitchens & Architectural Cabinetry South Wales & UK",
        "lighthouse_score": 40,
        "lcp_ms": 5900,
        "tbt_ms": 650,
        "variant": "B"
    },
    {
        "company": "AKM Bespoke Joinery",
        "url": "https://akmbespoke.co.uk",
        "email": "info@akmbespoke.co.uk",
        "contact_name": "AKM Bespoke Joinery",
        "role": "Architectural Joinery & Bespoke Furniture Makers UK",
        "lighthouse_score": 39,
        "lcp_ms": 6000,
        "tbt_ms": 660,
        "variant": "A"
    },
    {
        "company": "Derbyshire Kitchen Company",
        "url": "https://derbyshirekitchencompany.co.uk",
        "email": "hello@derbyshirekitchencompany.co.uk",
        "contact_name": "Derbyshire Kitchen Company",
        "role": "Luxury Bespoke Kitchens & Living Spaces Derbyshire UK",
        "lighthouse_score": 41,
        "lcp_ms": 5800,
        "tbt_ms": 630,
        "variant": "B"
    },
    {
        "company": "Derbyshire Bespoke Interiors",
        "url": "https://derbyshirekitchens.co.uk",
        "email": "sales@derbyshirekitchens.co.uk",
        "contact_name": "Derbyshire Bespoke Interiors",
        "role": "Custom Handcrafted Kitchens & Bespoke Furniture Derbyshire UK",
        "lighthouse_score": 37,
        "lcp_ms": 6300,
        "tbt_ms": 690,
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

print(f"Successfully wrote {len(rows)} leads to data/outreach_queue.csv for Batch 73:")
for r in rows:
    print(f"{r['company']} | {r['email']} | {r['variant']} | {r['subject']}")
