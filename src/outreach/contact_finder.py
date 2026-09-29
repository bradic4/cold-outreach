import re
from urllib.parse import urljoin, urlparse
import requests


class ContactFinder:
    EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    PAGES = ("", "/contact", "/contact-us", "/about", "/about-us", "/team", "/people")
    BAD = ("example.com", "sentry.io", "wixpress.com", "wordpress.org", "elementor.com")
    BAD_TLDS = {
        "png", "jpg", "jpeg", "webp", "svg", "gif", "bmp", "ico",
        "css", "js", "woff", "woff2", "ttf", "eot", "mp4", "mp3",
        "pdf", "zip", "tar", "gz", "html", "php", "ashx", "aspx"
    }
    ROLE_SCORES = {
        "director": 100, "owner": 100, "founder": 100, "partner": 95, "principal": 95,
        "marketing": 75, "business": 70, "sales": 65, "office": 50, "info": 40, "hello": 40, "support": 20
    }
    GENERIC_LOCALS = {
        "info", "office", "enquiries", "enquiry", "admin", "contact", "contacts",
        "hello", "mail", "general", "reception", "london", "manchester", "birmingham",
        "uk", "studio", "support", "help", "press", "media", "sales"
    }

    def __init__(self, timeout=8):
        self.timeout = timeout
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; OutreachQualification/3.3)"}

    def _extract_name_and_role(self, email, text):
        local = email.split("@")[0].lower()
        around = text.lower()

        # Check if local part is a generic inbox
        is_generic = local in self.GENERIC_LOCALS or not local.replace(".", "").isalpha()

        contact_name = ""
        first_name = ""
        role = ""
        score = 35

        if is_generic:
            role = local if local in ("info", "office", "enquiries", "hello", "support") else "general"
            score = 45 if role in ("office", "enquiries") else 40
            # Only elevate generic inbox if there's a strict direct label right next to email
            for key in ("director", "owner", "founder", "partner", "principal"):
                if re.search(rf"\b{key}\b\s*[:\-–]?\s*{re.escape(email)}", text, re.I):
                    score, role = self.ROLE_SCORES[key], key
                    break
            return score, role, contact_name, first_name

        # Personal email address
        score = 65 if "." in local else 55
        # Parse potential name from local part
        if "." in local:
            parts = local.split(".")
            if len(parts) >= 2 and parts[0].isalpha() and parts[1].isalpha():
                first_name = parts[0].capitalize()
                contact_name = f"{parts[0].capitalize()} {parts[1].capitalize()}"
        elif len(local) > 2 and local.isalpha():
            first_name = local.capitalize()
            contact_name = local.capitalize()

        # Look for explicit name and role in nearby text
        name_match = re.search(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+))\b\s*(?:[,|\-•]\s*)?\b(Director|Founder|Owner|Partner|Principal|Architect)\b", text)
        if name_match:
            contact_name = name_match.group(1).strip()
            first_name = contact_name.split()[0]
            matched_role = name_match.group(2).lower()
            if matched_role in self.ROLE_SCORES:
                score, role = self.ROLE_SCORES[matched_role], matched_role

        if not role:
            for key, points in self.ROLE_SCORES.items():
                if key in local:
                    score, role = points, key
                    break
                elif key in around and points >= 90:
                    score, role = points, key
                    break

        return score, role, contact_name, first_name

    def _score(self, email, text):
        score, role, _, _ = self._extract_name_and_role(email, text)
        return score, role

    def find(self, url, company_name=""):
        candidates = {}
        for suffix in self.PAGES:
            page = url if not suffix else urljoin(url, suffix)
            try:
                r = requests.get(page, headers=self.headers, timeout=self.timeout, verify=False)
                if r.status_code != 200:
                    continue
                for m in self.EMAIL_RE.finditer(r.text):
                    email = m.group(0).lower().strip()
                    tld = email.split(".")[-1].lower()
                    if tld in self.BAD_TLDS or "@2x" in email or "@3x" in email or "@1x" in email:
                        continue
                    if any(x in email for x in self.BAD):
                        continue
                    context = re.sub(r"<[^>]+>", " ", r.text[max(0, m.start() - 250):m.end() + 250])
                    score, role, name, first_name = self._extract_name_and_role(email, context)
                    old = candidates.get(email)
                    if not old or score > old["contact_score"]:
                        candidates[email] = {
                            "email": email,
                            "role": role,
                            "name": name,
                            "first_name": first_name,
                            "source_url": page,
                            "contact_score": score,
                        }
            except requests.RequestException:
                continue

        if not candidates:
            return {"email": "", "role": "", "name": "", "first_name": "", "source_url": "", "contact_score": 0, "contact_confidence": "none"}

        best = max(candidates.values(), key=lambda x: x["contact_score"])
        best["contact_confidence"] = "high" if best["contact_score"] >= 75 else "medium" if best["contact_score"] >= 50 else "low"

        # Eponymous company name fallback if first_name not yet set
        if not best.get("first_name") and company_name:
            words = [w for w in company_name.split() if w.isalpha()]
            suffixes = ("architects", "architecture", "design", "studio", "associates", "partners", "practice", "consulting")
            if len(words) >= 3 and words[-1].lower() in suffixes and words[-2].lower() not in suffixes:
                first, last = words[0], words[1]
                non_person = ("ck", "nada", "epr", "manchester", "london", "urban", "rural", "modern", "green", "city")
                if first.lower() not in non_person and len(first) > 2:
                    best["first_name"] = first.capitalize()
                    best["name"] = f"{first.capitalize()} {last.capitalize()}"
            elif len(words) == 2 and words[-1].lower() in suffixes:
                first = words[0]
                if len(first) > 2 and first.lower() not in ("ck", "nada", "epr", "city", "urban"):
                    best["first_name"] = first.capitalize()
                    best["name"] = first.capitalize()

        return best
