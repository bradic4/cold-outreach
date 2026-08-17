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
            "facebook.com", "instagram.com", "youtube.com", "linkedin.com", "tiktok.com",
            "wikipedia.org", "yellowpages.com", "tripadvisor.com", "booking.com", 
            "kupujemprodajem.com", "halooglasi.com", "planplus.rs", "nadjidom.com", 
            "mojgrad.rs", "bing.com", "microsoft.com", "google.com", "mirandre.com", "navidiku.rs",
            "4zida.rs", "infostud.com", "inspira.rs", "nekretnine.rs", "oglasi.rs", 
            "cityexpert.rs", "011info.com", "daibau.rs", "daibau.ba", "ekapija.com", "portal-srbija.com", 
            "firmesrbije.com", "pttimenik.com", "superprostor.com", "drbook.rs", "gohome.rs", 
            "berzanekretnina.org", "realitica.com", "moj-majstor.rs", "kredium.rs", "haoss.org", 
            "radiopingvin.com", "klikdofirme.com", "iskustva.online", "apartmani-u-beogradu.com", 
            "carrentalbeograd.rs", "eistra.info", "cu.rs", "vslpu.edu.rs", "fsu.edu.rs", "ytong.com",
            "stambeno.com", "infostan.rs", "posta.rs", "eps.rs", "pks.rs", "beograd.rs",
            "jkp.rs", "jp.rs", "skupstina.rs", "voda.rs", "elektrane.rs", "kayak.com", "expedia.com",
            "skyscanner.com", "rentalcars.com", "polovniautomobili.com", "polovniautomobili.rs", "mojauto.rs",
            "checkatrade.com", "trustatrader.com", "yell.com", "cylex-uk.co.uk", "threebestrated.co.uk",
            "njuskalo.hr", "mojkvart.hr", "moja-djelatnost.hr", "tvrtke.hr", "pronadji.ba", "doma.ba",
            "yandex.com", "maps.yandex.ru", "autoservisisrbija.rs", "e-usluga.rs", "poslovne-strane.rs",
            "biznisgroup.com", "infostar.rs", "krakendesign.rs", "lupostudio.rs",
            "soloherc.rs", "soloherc.co.rs", "soloherc.com", "soloherc.net", "solo-herc.rs", "soloherc",
            "beogradski.press", "firma.co.rs", "mojakompanija.rs", "ls.rs", "autentik.net", "yumpu.com",
            "scribd.com", "pdfcoffee.com", "polazak.rs", "arte.rs", "kreativnomentorstvo.com", "journal.rs",
            "ozon.rs", "jub.rs", "jub.si", "jub.hr", "jub.ba", "wannabemagazine.com", "mpus.org.rs", "uklo.edu.mk",
            "registarfirmi.me", "moja-djelatnost.me", "busticket4.me", "ajpes.si", "si21.com"
        ]

        try:
            from ddgs import DDGS
            for retry in range(3):
                try:
                    with DDGS(timeout=15) as ddgs:
                        results = list(ddgs.text(query, region="rs-sr", max_results=limit * 2))
                        for r in results:
                            u = r.get("href", "").strip()
                            u_lower = u.lower()
                            if u and not any(ex in u_lower for ex in excluded) and not (".gov.rs" in u_lower or ".ac.rs" in u_lower or ".edu.rs" in u_lower):
                                if u not in urls:
                                    urls.append(u)
                                    if len(urls) >= limit:
                                        break
                        if urls:
                            break
                except Exception as inner_e:
                    time.sleep(1)
        except Exception as e:
            warning(f"Pretraga nije uspela: {e}")

        # Fallback multi-engine SERP Scraper (Bing & DuckDuckGo HTML) if DDGS timed out
        if not urls:
            search_urls = [
                f"https://www.bing.com/search?q={requests.utils.quote(query)}",
                f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            ]
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            for s_url in search_urls:
                try:
                    resp = requests.get(s_url, headers=headers, timeout=10)
                    if resp.status_code == 200:
                        found_urls = re.findall(r'href="(https?://[^"]+)"', resp.text)
                        for u in found_urls:
                            u_clean = u.split("&")[0].split("?")[0].strip()
                            u_lower = u_clean.lower()
                            if u_clean and not any(ex in u_lower for ex in excluded) and not any(x in u_lower for x in ["duckduckgo.com", "bing.com", "microsoft.com", ".gov.rs", ".ac.rs", ".edu.rs"]):
                                if u_clean not in urls:
                                    urls.append(u_clean)
                                    if len(urls) >= limit:
                                        break
                        if urls:
                            break
                except Exception:
                    continue

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
                        invalid_patterns = [
                            "example.com", "example@", "vas@email.com", "your.address@email.com", "user@domain.com", 
                            "your@email.com", "john.doe", "jane.doe", "sentry.io", "wixpress.com", "schema.org", 
                            "w3.org", "wordpress.org", "wp.com", "elementor.com", "themeforest.net", "bootstrapmade.com",
                            "sentry-next", "ingest.de.sentry", "redakcija@", "urednik@", "press@", "marketing@ns-group",
                            "azma@verat", "taxi.mne"
                        ]
                        if any(p in em_lower for p in invalid_patterns):
                            continue
                        if not any(em_lower.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".svg", ".js", ".css", ".gif"]):
                            return em.strip()
            except Exception:
                continue
        return ""

    def is_valid_mx(self, email: str) -> bool:
        """
        Verify if the email domain has active DNS MX records.
        """
        try:
            if not email or "@" not in email:
                return False
            domain = email.split("@")[1].strip().lower()
            
            bogus_domains = [
                "sentry.io", "wixpress.com", "example.com", "domain.com", "email.com", "schema.org", "w3.org",
                "png", "jpg", "jpeg", "webp", "svg", "js", "css", "gif", "htm", "html", "pdf", "doc", "docx",
                "registarfirmi.me", "moja-djelatnost.me", "beogradski.press", "firma.co.rs"
            ]
            if any(b in domain for b in bogus_domains):
                return False

            import dns.resolver
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8', '1.1.1.1']
            resolver.timeout = 3
            resolver.lifetime = 3
            answers = resolver.resolve(domain, "MX")
            return len(answers) > 0
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            return False
        except Exception:
            try:
                import socket
                domain = email.split("@")[1].strip().lower()
                socket.gethostbyname(domain)
                return True
            except Exception:
                return False

    def start(self) -> None:
        """
        Start automated outreach flow.
        """
        # Daily cap check at the very start of run()
        import json
        from datetime import date
        today_str = date.today().isoformat()
        daily_stats_file = os.path.join(ROOT_DIR, ".mp", "daily_outreach_stats.json")
        daily_count = 0
        if os.path.exists(daily_stats_file):
            try:
                with open(daily_stats_file, "r", encoding="utf-8") as dsf:
                    stats_data = json.load(dsf)
                    if stats_data.get("date") == today_str:
                        daily_count = stats_data.get("count", 0)
            except Exception:
                daily_count = 0

        if daily_count >= 20:
            warning(f"🛑 Dostignut maksimalni bezbednosni DNEVNI limit od 20 poslatih mejlova za danas ({today_str}). Slanje je u potpunosti pauzirano radi očuvanja reputacije naloga!")
            return

        websites = self.search_business_websites(self.niche, limit=30)
        if not websites:
            error("Nijedan sajt nije pronađen. Proveri pretragu u config.json.")
            return

        with open(os.path.join(ROOT_DIR, self.body_file), "r", encoding="utf-8") as f:
            raw_body = f.read()

        smtp_server = self.email_creds.get("smtp_server", "smtp-mail.outlook.com")
        smtp_port = int(self.email_creds.get("smtp_port", 587))
        user_email = self.email_creds.get("username", "")
        user_pass = self.email_creds.get("password", "")

        sent_count = 0
        output_csv = get_results_cache_path()
        history_file = os.path.join(ROOT_DIR, ".mp", "sent_emails_history.txt")
        os.makedirs(os.path.dirname(history_file), exist_ok=True)

        def get_root_domain(url_or_email: str) -> str:
            text = url_or_email.lower().replace("http://", "").replace("https://", "").replace("www.", "").split("/")[0].split(":")[0].strip()
            if "@" in text:
                text = text.split("@")[1]
            parts = text.split(".")
            if len(parts) >= 3 and parts[-2] in ["co", "org", "in", "edu", "ac", "gov", "com", "net", "biz"]:
                return ".".join(parts[-3:])
            elif len(parts) >= 2:
                return ".".join(parts[-2:])
            return text

        sent_history = set()
        sent_domains = set()
        sent_prefixes = set()

        if os.path.exists(history_file):
            with open(history_file, "r", encoding="utf-8") as hf:
                for line in hf:
                    cleaned_item = line.strip().lower()
                    if cleaned_item:
                        sent_history.add(cleaned_item)
                        root_dom = get_root_domain(cleaned_item)
                        if root_dom:
                            sent_domains.add(root_dom)
                        if "@" in cleaned_item:
                            user_prefix = cleaned_item.split("@")[0].strip()
                            clean_prefix = re.sub(r"\d+$", "", user_prefix)
                            if len(clean_prefix) > 4:
                                sent_prefixes.add(clean_prefix)

        with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Website", "Email", "Status"])

            for idx, site in enumerate(websites, 1):
                info(f"[{idx}/{len(websites)}] Analiziram sajt: {site}")
                
                site_domain = ""
                site_domain_match = re.search(r"https?://(?:www\.)?([^/]+)", site.lower())
                if site_domain_match:
                    site_domain = site_domain_match.group(1).strip()

                site_root = get_root_domain(site)

                if (site_domain and (site_domain in sent_domains or site_domain in sent_history)) or (site_root and site_root in sent_domains):
                    warning(f"  ⚠️ Sajt/Domen {site_domain} (koren: {site_root}) je već dobio ponudu ranije. Preskačem duplikat...")
                    writer.writerow([site, "", "Already Sent (Domain)"])
                    continue

                email_addr = self.extract_email_from_website(site).strip().lower()
                
                if not email_addr:
                    warning(f"  ❌ Nema email-a na sajtu {site}")
                    writer.writerow([site, "", "No email"])
                    continue

                email_domain = email_addr.split("@")[1].strip() if "@" in email_addr else ""
                email_root = get_root_domain(email_addr)
                email_prefix = re.sub(r"\d+$", "", email_addr.split("@")[0].strip()) if "@" in email_addr else ""

                if (
                    email_addr in sent_history 
                    or (email_domain and email_domain in sent_domains) 
                    or (email_root and email_root in sent_domains) 
                    or (site_domain and site_domain in sent_domains)
                    or (site_root and site_root in sent_domains)
                    or (len(email_prefix) > 4 and email_prefix in sent_prefixes)
                ):
                    warning(f"  ⚠️ Email/Domen {email_addr} (koren: {email_root}) je već dobio ponudu ranije. Preskačem duplikat...")
                    writer.writerow([site, email_addr, "Already Sent"])
                    continue

                if not self.is_valid_mx(email_addr):
                    warning(f"  ⚠️ Neaktivan mail server za {email_addr} (MX ne reaguje). Preskačem...")
                    writer.writerow([site, email_addr, "Invalid MX"])
                    continue

                info(f"  Pronađen aktivan email: {email_addr}. Šaljem ponudu...")
                try:
                    company_name = "biznis"
                    if site_domain:
                        company_name = site_domain.split(".")[0].capitalize()

                    # Aggregator / News / Non-direct business domain filter
                    junk_domains = ["jutarnji.hr", "blic.rs", "kupujemprodajem.org", "estitor.com", "telegraf.rs", "espreso.co.rs", "edukacija.rs", "srbija-nekretnine.org", "oglasi-srbija.com", "pinterest.com", "youtube.com", "facebook.com", "instagram.com", "linkedin.com", "tiktok.com", "wikipedia.org"]
                    if any(jd in (site_domain or "").lower() for jd in junk_domains):
                        warning(f"  ⚠️ Preskačem vesti/agregat sajt: {site}")
                        writer.writerow([site, email_addr, "Skipped Aggregator"])
                        continue

                    # Daily cap check (max 20 per calendar day)
                    import json
                    from datetime import date
                    today_str = date.today().isoformat()
                    daily_stats_file = os.path.join(ROOT_DIR, ".mp", "daily_outreach_stats.json")
                    daily_count = 0
                    if os.path.exists(daily_stats_file):
                        try:
                            with open(daily_stats_file, "r", encoding="utf-8") as dsf:
                                stats_data = json.load(dsf)
                                if stats_data.get("date") == today_str:
                                    daily_count = stats_data.get("count", 0)
                        except Exception:
                            daily_count = 0

                    if daily_count >= 20:
                        warning(f"  🛑 Dostignut maksimalni bezbednosni DNEVNI limit od 20 poslatih mejlova za {today_str}. Pauziramo slanje za danas radi potpunog očuvanja Gmail reputacije!")
                        break

                    subj = self.subject.replace("{{COMPANY_NAME}}", company_name)
                    body = raw_body.replace("{{COMPANY_NAME}}", company_name)

                    import smtplib
                    from email.mime.text import MIMEText
                    from email.mime.multipart import MIMEMultipart

                    msg = MIMEMultipart("alternative")
                    msg["From"] = f"Ivan Bradić <{user_email}>"
                    msg["To"] = email_addr
                    msg["Subject"] = subj
                    msg.attach(MIMEText(body, "html", "utf-8"))

                    if smtp_port == 465:
                        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=15) as server:
                            server.login(user_email, user_pass)
                            server.sendmail(user_email, email_addr, msg.as_string())
                    else:
                        with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
                            server.ehlo()
                            server.starttls()
                            server.ehlo()
                            server.login(user_email, user_pass)
                            server.sendmail(user_email, email_addr, msg.as_string())

                    success(f"  ✅ Uspešno poslato na {email_addr} ({company_name})!")
                    writer.writerow([site, email_addr, "Sent"])
                    sent_count += 1
                    
                    # Record sent email and domain in history
                    sent_history.add(email_addr)
                    if email_domain:
                        sent_domains.add(email_domain)
                    if email_root:
                        sent_domains.add(email_root)
                    if site_domain:
                        sent_domains.add(site_domain)
                    if site_root:
                        sent_domains.add(site_root)
                    if len(email_prefix) > 4:
                        sent_prefixes.add(email_prefix)

                    with open(history_file, "a", encoding="utf-8") as hf:
                        hf.write(email_addr + "\n")
                        if site_domain:
                            hf.write(site_domain + "\n")
                        if site_root and site_root != site_domain:
                            hf.write(site_root + "\n")

                    # Update daily counter
                    daily_count += 1
                    try:
                        with open(daily_stats_file, "w", encoding="utf-8") as dsf:
                            json.dump({"date": today_str, "count": daily_count}, dsf)
                    except Exception:
                        pass

                    info(f"  ⏳ Čekam 20 sekundi (ljudski tempo) pre sledećeg slanja... (Danas poslato: {daily_count}/20)")
                    time.sleep(20)

                    if sent_count >= 3:
                        info("  🛑 Dostignut bezbednosni limit od 3 poslata mejla po turi (zaštita naloga). Pauziram...")
                        break
                except Exception as err:
                    error(f"  ❌ Greška pri slanju na {email_addr}: {err}")
                    writer.writerow([site, email_addr, f"Error: {err}"])

        success(f"\nOutreach završen! Uspešno poslato {sent_count} mejlova.")
