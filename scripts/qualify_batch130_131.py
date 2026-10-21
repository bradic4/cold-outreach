import sys
import os
import requests
import urllib3
urllib3.disable_warnings()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classes.Outreach import Outreach
from outreach.mailer import verify_mailbox_smtp

outreach = Outreach()

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as f:
        sent_history = {l.strip().lower() for l in f if l.strip()}

candidates = [
    ("Grange Craft", "https://grangecraft.ie", "info@grangecraft.ie", "Bespoke Handcrafted Kitchens Cork Ireland"),
    ("Dillons Kitchens", "https://dillonskitchens.ie", "info@dillonskitchens.ie", "Bespoke Kitchens & Bedrooms Tipperary Ireland"),
    ("Northern Kitchens", "https://northernkitchens.com.au", "info@northernkitchens.com.au", "Custom Kitchen Joinery Brisbane Australia"),
    ("Finewood Designer Kitchens", "https://finewooddesignerkitchens.com.au", "info@finewooddesignerkitchens.com.au", "Custom Designer Kitchens Melbourne Australia"),
    ("Wood Wizards Kitchens", "https://woodwizardskitchens.com.au", "jordan@woodwizardskitchens.com.au", "Custom Kitchen Design & Cabinetry Melbourne Australia"),
    ("Touchwood Cabinetry", "https://touchwood.com.au", "sales@touchwood.com.au", "Custom Cabinetry & Kitchens Melbourne Australia"),
    ("Melbournian Kitchens", "https://melbourniankitchens.com.au", "info@melbourniankitchens.com.au", "Custom Built Bespoke Kitchens Melbourne Australia"),
    ("Sagar Cabinets", "https://sagarcabinets.com.au", "info@sagarcabinets.com.au", "Bespoke Custom Cabinetry Melbourne Australia"),
    ("Elite Custom Cabinetry", "https://elitecustomcabinetry.com.au", "info@elitecustomcabinetry.com.au", "Custom Cabinetry & Kitchens Brisbane Australia"),
    ("Custom Cabinetry Brisbane", "https://customcabinetrybrisbane.com.au", "enquiry@customcabinetrybrisbane.com.au", "Custom Cabinetry & Kitchen Renovations Brisbane Australia"),
    ("iMake Interiors", "https://imakeinteriors.com.au", "info@imakeinteriors.com.au", "Bespoke Kitchens & Custom Joinery Brisbane Australia"),
    ("Forma Fine Cabinetry", "https://formakitchen.ca", "info@formagroup.ca", "Custom High-End Cabinetry Toronto Canada"),
    ("Platinum Group", "https://platinumgroupinc.ca", "info@platinumgroupinc.ca", "Custom Kitchen Cabinets & Millwork Toronto Canada"),
    ("Maxwood Kitchen", "https://maxwoodcanada.ca", "info@maxwoodcanada.ca", "Custom Cabinetry & Kitchen Design Scarborough Canada"),
    ("Jatoba Kitchens", "https://jatobakitchens.ca", "info@jatobakitchens.ca", "Custom Kitchens & Architectural Millwork Mississauga Canada")
]

passed = []

for comp, url, em, role in candidates:
    em_low = em.lower().strip()
    dom = url.split("//")[-1].split("/")[0].replace("www.", "").lower().strip()
    
    if em_low in sent_history or dom in sent_history:
        print(f"{comp}: ALREADY IN HISTORY")
        continue
    
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, verify=False)
        if r.status_code >= 400:
            print(f"{comp}: HTTP {r.status_code}")
            continue
    except Exception as e:
        print(f"{comp}: HTTP ERROR {e}")
        continue
    
    if not outreach.is_valid_mx(em_low):
        print(f"{comp}: MX FAIL")
        continue
    
    if not verify_mailbox_smtp(em_low, sender_addr="ivanbradic.biz@gmail.com"):
        print(f"{comp}: SMTP FAIL")
        continue
    
    print(f"PASS: {comp} | {url} | {em_low}")
    passed.append((comp, url, em, role))

print(f"\n==========================================")
print(f"TOTAL PASSED: {len(passed)}")
for p in passed:
    print(f"- {p[0]} ({p[2]}) | {p[1]} | {p[3]}")
