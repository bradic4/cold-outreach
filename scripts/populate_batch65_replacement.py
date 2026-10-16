import csv
import os

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as hf:
        sent_history = {line.strip().lower() for line in hf if line.strip()}

lead = {
    "company": "Nicholas Moody Kitchens",
    "url": "https://nicholasmoodykitchens.com",
    "email": "nick@nicholasmoodykitchens.com",
    "contact_name": "Nick",
    "role": "Bespoke Kitchen Design & Handcrafted Cabinetry Ireland",
    "lighthouse_score": 39,
    "lcp_ms": 6000,
    "tbt_ms": 670,
    "variant": "B"
}

em = lead["email"].strip().lower()
dom = lead["url"].split("//")[-1].split("/")[0].replace("www.", "").lower()
if em in sent_history:
    raise ValueError(f"Email {em} already in history!")
if dom in sent_history:
    raise ValueError(f"Domain {dom} already in history!")

body_template = """Hi,

I had a look at your company's website and noticed a few things that could be improved, especially when potential clients open it on their mobile phone.

For bespoke kitchen and joinery companies, the website is usually the first point of contact with a future client. That's why it's important that it quickly showcases your work and services and makes it effortless for visitors to get in touch.

I specialize in website optimization and have a few specific ideas on how you could improve the mobile experience and increase enquiries.

I can send over a short free breakdown with the 3 things I'd change first.

Would you like to take a look at it?

Best,
Ivan Bradić
ivanbradic.vercel.app"""

subj = f"Quick question about {lead['company']}'s website"

row = {
    "company": lead["company"],
    "url": lead["url"],
    "email": lead["email"],
    "contact_name": lead["contact_name"],
    "first_name": "Nick",
    "role": lead["role"],
    "lighthouse_score": lead["lighthouse_score"],
    "lcp_ms": lead["lcp_ms"],
    "tbt_ms": lead["tbt_ms"],
    "variant": lead["variant"],
    "subject": subj,
    "message": body_template,
    "status": "ready"
}

fieldnames = ["company", "url", "email", "contact_name", "first_name", "role", "lighthouse_score", "lcp_ms", "tbt_ms", "variant", "subject", "message", "status"]
with open("data/outreach_queue.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow(row)

print("Successfully wrote replacement lead to data/outreach_queue.csv:")
print(f"{row['company']} | {row['email']} | {row['variant']} | {row['subject']}")
