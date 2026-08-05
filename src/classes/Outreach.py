import os
import re
import csv
import time
import urllib3
import requests
import yagmail

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from config import (
    get_google_maps_scraper_niche,
    get_outreach_message_subject,
    get_outreach_message_body_file,
    get_email_credentials,
    ROOT_DIR,
)
from cache import get_results_cache_path
from status import info, success, warning, error


class Outreach:
    """
    Python-native Outreach automator.
    Finds business websites via web search, extracts contact emails, and sends outreach emails.
    """

    def __init__(self) -> None:
        self.niche = get_google_maps_scraper_niche()
        self.email_creds = get_email_credentials()
        self.subject = get_outreach_message_subject()
        self.body_file = get_outreach_message_body_file()

    def search_business_websites(self, query: str, limit: int = 30) -> list[str]:
        """
        Search DuckDuckGo API for business websites matching the query.
        """
        info(f"Tražim lokalne biznise i sajtove na web-u za: '{query}'...")
        urls = []
        excluded = [
            "facebook.com", "instagram.com", "youtube.com", "linkedin.com", 
            "wikipedia.org", "yellowpages.com", "tripadvisor.com", "booking.com", 
            "kupujemprodajem.com", "halooglasi.com", "planplus.rs", "nadjidom.com", 
            "mojgrad.rs", "bing.com", "microsoft.com", "google.com", "mirandre.com", "navidiku.rs"
        ]

        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=limit * 2))
                for r in results:
                    u = r.get("href", "").strip()
                    if u and not any(ex in u.lower() for ex in excluded):
                        if u not in urls:
                            urls.append(u)
                            if len(urls) >= limit:
                                break
        except Exception as e:
            warning(f"Pretraga nije uspela: {e}")

        success(f"Pronađeno {len(urls)} jedinstvenih sajtova biznisa!")
        return urls

    def extract_email_from_website(self, website_url: str) -> str:
        """
        Scrape a website and find contact email.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
        
        pages_to_check = [website_url]
        base_domain = website_url.rstrip("/")
        pages_to_check.extend([f"{base_domain}/kontakt", f"{base_domain}/contact", f"{base_domain}/about-us", f"{base_domain}/o-nama"])

        for page_url in pages_to_check:
            try:
                r = requests.get(page_url, headers=headers, verify=False, timeout=8)
                if r.status_code == 200:
                    found = re.findall(email_pattern, r.text)
                    for em in found:
                        em_lower = em.lower()
                        # Ignore placeholder and image/file extensions matched as email domain
                        if any(p in em_lower for p in ["example.com", "example@", "vas@email.com", "your.address@email.com", "user@domain.com"]):
                            continue
                        if not any(em_lower.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".svg", ".js", ".css", ".gif"]):
                            return em
            except Exception:
                continue
        return ""

    def is_valid_mx(self, email: str) -> bool:
        """
        Verify if the email domain has active DNS MX records.
        """
        try:
            domain = email.split("@")[1].strip()
            import dns.resolver
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8', '1.1.1.1']
            resolver.timeout = 4
            resolver.lifetime = 4
            answers = resolver.resolve(domain, "MX")
            return len(answers) > 0
        except Exception:
            return True

    def start(self) -> None:
        """
        Start automated outreach flow.
        """
        websites = self.search_business_websites(self.niche, limit=30)
        if not websites:
            error("Nijedan sajt nije pronađen. Proveri pretragu u config.json.")
            return

        with open(os.path.join(ROOT_DIR, self.body_file), "r", encoding="utf-8") as f:
            raw_body = f.read()

        yag = yagmail.SMTP(
            user=self.email_creds["username"],
            password=self.email_creds["password"],
            port=465,
        )

        sent_count = 0
        output_csv = get_results_cache_path()
        history_file = os.path.join(ROOT_DIR, ".mp", "sent_emails_history.txt")
        os.makedirs(os.path.dirname(history_file), exist_ok=True)

        sent_history = set()
        if os.path.exists(history_file):
            with open(history_file, "r", encoding="utf-8") as hf:
                for line in hf:
                    if line.strip():
                        sent_history.add(line.strip().lower())

        with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Website", "Email", "Status"])

            for idx, site in enumerate(websites, 1):
                info(f"[{idx}/{len(websites)}] Analiziram sajt: {site}")
                email_addr = self.extract_email_from_website(site)
                
                if not email_addr:
                    warning(f"  ❌ Nema email-a na sajtu {site}")
                    writer.writerow([site, "", "No email"])
                    continue

                if email_addr.lower() in sent_history:
                    warning(f"  ⚠️ Email {email_addr} je već dobio ponudu ranije. Preskačem duplikat...")
                    writer.writerow([site, email_addr, "Already Sent"])
                    continue

                if not self.is_valid_mx(email_addr):
                    warning(f"  ⚠️ Neaktivan mail server za {email_addr} (MX ne reaguje). Preskačem...")
                    writer.writerow([site, email_addr, "Invalid MX"])
                    continue

                info(f"  Pronađen aktivan email: {email_addr}. Šaljem ponudu...")
                try:
                    company_name = "biznis"
                    # Extract domain name as fallback company name
                    domain_match = re.search(r"https?://(?:www\.)?([^/]+)", site)
                    if domain_match:
                        company_name = domain_match.group(1).split(".")[0].capitalize()

                    subj = self.subject.replace("{{COMPANY_NAME}}", company_name)
                    body = raw_body.replace("{{COMPANY_NAME}}", company_name)

                    yag.send(to=email_addr, subject=subj, contents=body)
                    success(f"  ✅ Uspešno poslato na {email_addr} ({company_name})")
                    writer.writerow([site, email_addr, "Sent"])
                    sent_count += 1
                    
                    # Record sent email in history
                    sent_history.add(email_addr.lower())
                    with open(history_file, "a", encoding="utf-8") as hf:
                        hf.write(email_addr.lower() + "\n")

                    time.sleep(2)
                except Exception as err:
                    error(f"  ❌ Greška pri slanju na {email_addr}: {err}")
                    writer.writerow([site, email_addr, f"Error: {err}"])

        success(f"\nOutreach završen! Uspešno poslato {sent_count} mejlova.")
