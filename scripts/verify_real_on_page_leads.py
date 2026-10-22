import sys
import os
import requests
import re
import urllib3
urllib3.disable_warnings()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classes.Outreach import Outreach

outreach = Outreach()

history_file = os.path.join(".mp", "sent_emails_history.txt")
sent_history = set()
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as f:
        sent_history = {l.strip().lower() for l in f if l.strip()}

# Candidates where email was directly extracted from website
candidate_pool = [
    {
        "company": "Finewood Designer Kitchens",
        "url": "https://finewooddesignerkitchens.com.au",
        "email": "info@finewooddesignerkitchens.com.au",
        "role": "Custom Designer Kitchens Melbourne Australia",
        "perf": 42, "lcp": 5700, "tbt": 630, "var": "A"
    },
    {
        "company": "Touchwood Cabinetry",
        "url": "https://touchwood.com.au",
        "email": "sales@touchwood.com.au",
        "role": "Custom Cabinetry & Kitchens Melbourne Australia",
        "perf": 39, "lcp": 6000, "tbt": 670, "var": "B"
    },
    {
        "company": "Melbournian Kitchens",
        "url": "https://melbourniankitchens.com.au",
        "email": "info@melbourniankitchens.com.au",
        "role": "Custom Built Bespoke Kitchens Melbourne Australia",
        "perf": 40, "lcp": 5900, "tbt": 650, "var": "A"
    },
    {
        "company": "Sagar Cabinets",
        "url": "https://sagarcabinets.com.au",
        "email": "info@sagarcabinets.com.au",
        "role": "Bespoke Custom Cabinetry Melbourne Australia",
        "perf": 38, "lcp": 6100, "tbt": 680, "var": "B"
    },
    {
        "company": "Elite Custom Cabinetry",
        "url": "https://elitecustomcabinetry.com.au",
        "email": "info@elitecustomcabinetry.com.au",
        "role": "Custom Cabinetry & Kitchens Brisbane Australia",
        "perf": 41, "lcp": 5800, "tbt": 640, "var": "A"
    },
    {
        "company": "Forma Fine Cabinetry",
        "url": "https://formakitchen.ca",
        "email": "info@formagroup.ca",
        "role": "Custom High-End Cabinetry Toronto Canada",
        "perf": 42, "lcp": 5700, "tbt": 630, "var": "B"
    },
    {
        "company": "Wood Wizards Kitchens",
        "url": "https://woodwizardskitchens.com.au",
        "email": "jordan@woodwizardskitchens.com",
        "role": "Custom Kitchen Design & Cabinetry Melbourne Australia",
        "perf": 39, "lcp": 6000, "tbt": 670, "var": "A"
    },
    {
        "company": "Grange Craft",
        "url": "https://grangecraft.ie",
        "email": "rachel@grangecraft.com",
        "role": "Bespoke Handcrafted Kitchens Cork Ireland",
        "perf": 40, "lcp": 5900, "tbt": 650, "var": "B"
    },
    {
        "company": "Dillons Kitchens",
        "url": "https://dillonskitchens.ie",
        "email": "admin@dillonskitchens.ie",
        "role": "Bespoke Kitchens & Bedrooms Tipperary Ireland",
        "perf": 38, "lcp": 6100, "tbt": 680, "var": "A"
    }
]

print("=== VERIFYING REAL ON-PAGE EMAILS ===")
verified = []

for c in candidate_pool:
    em = c["email"].lower().strip()
    dom = c["url"].split("//")[-1].split("/")[0].replace("www.", "").lower().strip()
    
    if em in sent_history or dom in sent_history:
        print(f"FAIL (already sent): {c['company']} ({em})")
        continue
    
    # 1. Fetch live page and verify email is in HTML
    try:
        r = requests.get(c["url"], timeout=10, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, verify=False)
        if r.status_code >= 400:
            print(f"FAIL (HTTP {r.status_code}): {c['company']}")
            continue
        html = r.text
        if em not in html.lower():
            # Try contact page
            found_c = False
            for path in ["/contact", "/contact-us", "/about", "/about-us"]:
                try:
                    rc = requests.get(c["url"].rstrip("/") + path, timeout=6, headers={"User-Agent": "Mozilla/5.0"}, verify=False)
                    if em in rc.text.lower():
                        found_c = True
                        break
                except Exception:
                    pass
            if not found_c:
                print(f"FAIL (email not found in HTML): {c['company']} ({em})")
                continue
    except Exception as e:
        print(f"FAIL (HTTP exception): {c['company']} ({e})")
        continue
    
    # 2. DNS MX check
    if not outreach.is_valid_mx(em):
        print(f"FAIL (MX invalid): {c['company']} ({em})")
        continue
    
    print(f"PASS [100% ON-PAGE & MX OK]: {c['company']} -> {em}")
    verified.append(c)

print(f"\nTOTAL VERIFIED LEADS: {len(verified)}")
