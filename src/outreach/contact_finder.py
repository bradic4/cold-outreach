import re
from urllib.parse import urljoin, urlparse
import requests


class ContactFinder:
    EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    PAGES = ("", "/contact", "/contact-us", "/about", "/about-us", "/team", "/people", "/kontakt", "/o-nama", "/tim")
    BAD = (
        "example.com", "sentry.io", "wixpress.com", "wordpress.org", "elementor.com",
        "mail.com", "email.com", "domain.com", "yourdomain.com", "site.com", "yoursite.com",
        "example@", "test@", "user@", "username@", "yourname@"
    )
    BAD_TLDS = {
        "png", "jpg", "jpeg", "webp", "svg", "gif", "bmp", "ico",
        "css", "js", "woff", "woff2", "ttf", "eot", "mp4", "mp3",
        "pdf", "zip", "tar", "gz", "html", "php", "ashx", "aspx"
    }
    ROLE_SCORES = {
        "director": 100, "owner": 100, "founder": 100, "partner": 95, "principal": 95,
        "marketing": 75, "business": 70, "sales": 65, "office": 50, "info": 50, "hello": 50, "support": 20
    }
    GENERIC_LOCALS = {
        "info", "office", "enquiries", "enquiry", "inquiries", "inquiry",
        "admin", "contact", "contacts", "hello", "mail", "general", "reception",
        "welcome", "frontdesk", "desk", "central", "inbox", "connect", "hq",
        "london", "manchester", "birmingham", "leeds", "bristol", "liverpool",
        "aberdeen", "edinburgh", "glasgow", "cardiff", "belfast", "newcastle",
        "sheffield", "nottingham", "oxford", "cambridge", "york", "bath",
        "norwich", "exeter", "southampton", "plymouth", "derby", "leicester",
        "coventry", "hull", "bradford", "stoke", "wolverhampton", "swansea",
        "dundee", "inverness", "reading", "brighton", "bournemouth", "luton",
        "northampton", "miltonkeynes", "swindon", "westyorkshire", "yorkshire",
        "uk", "studio", "support", "help", "press", "media", "sales", "marketing",
        "recruitment", "recruit", "careers", "jobs", "work", "hr",
        "billing", "accounts", "finance", "legal", "privacy", "compliance",
        "team", "feedback", "post", "bookings", "booking", "architecture",
        "architects", "design", "projects", "commercial", "residential",
        "consult", "consulting", "customerservice", "customer", "directors", "partners", "management",
        "email", "home", "web", "online", "main", "solicitors", "solicitor", "law", "lawyers", "lawyer",
        "claims", "cases", "conveyancing", "litigation", "solihull", "maidstone", "leatherhead", "colmore"
    }
    PRIMARY_INBOXES = {
        "info", "office", "enquiries", "enquiry", "inquiries", "inquiry",
        "hello", "welcome", "contact", "contacts", "general", "reception", "studio",
        "email", "home", "mail", "kontakt", "prodaja", "agencija"
    }
    LOW_PRIORITY_INBOXES = {
        "recruitment", "recruit", "careers", "jobs", "work", "hr",
        "billing", "accounts", "finance", "legal", "privacy", "compliance",
        "support", "help", "press", "media"
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
            role = local if local in ("info", "office", "enquiries", "inquiries", "hello", "welcome", "support") else "general"
            if local in self.PRIMARY_INBOXES:
                score = 50 if role in ("office", "enquiries", "inquiries", "info", "hello", "welcome") else 45
            elif local in self.LOW_PRIORITY_INBOXES:
                score = 20
            else:
                score = 35
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
            if len(parts) >= 2 and len(parts[0]) > 1 and parts[0].isalpha() and parts[1].isalpha():
                first_name = parts[0].capitalize()
                contact_name = f"{parts[0].capitalize()} {parts[1].capitalize()}"
            elif len(parts) >= 2 and len(parts[0]) == 1 and parts[1].isalpha():
                first_name = ""
                contact_name = f"{parts[0].upper()} {parts[1].capitalize()}"
        elif len(local) > 2 and local.isalpha() and local not in self.GENERIC_LOCALS:
            is_initial_surname = (
                (len(local) >= 4 and local[0] == local[1]) or
                local.startswith(("mc", "mac")) or
                bool(re.search(r"^[a-z]mc[a-z]+$", local))
            )
            if not is_initial_surname:
                matched_prefix = False
                common_firsts = (
                    "ben", "john", "paul", "david", "mark", "alex", "sarah", "emma", "anna",
                    "tom", "chris", "james", "dan", "sam", "rob", "mike", "nick", "luke",
                    "richard", "adam", "simon", "tim", "steve", "matthew", "peter", "george",
                    "edward", "william", "michael", "andrew", "ian", "neil", "graham", "colin",
                    "brian", "alan", "kevin", "gary", "stephen", "philip", "martin", "anthony",
                    "judy", "lisa", "claire", "kate", "helen", "rachel", "lucy", "sophie"
                )
                for fn in common_firsts:
                    if local.startswith(fn) and len(local) - len(fn) >= 3:
                        first_name = fn.capitalize()
                        last_name = local[len(fn):].capitalize()
                        contact_name = f"{first_name} {last_name}"
                        matched_prefix = True
                        break
                if not matched_prefix:
                    if len(local) < 10:
                        first_name = local.capitalize()
                        contact_name = local.capitalize()
                    else:
                        first_name = ""
                        contact_name = ""

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

        if first_name and first_name.lower() in self.GENERIC_LOCALS:
            first_name = ""
        if contact_name and contact_name.lower() in self.GENERIC_LOCALS:
            contact_name = ""

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
            suffixes = ("architects", "architecture", "design", "studio", "associates", "partners", "practice", "consulting", "solicitors", "law", "legal", "lawyers")
            if len(words) >= 3 and words[-1].lower() in suffixes and words[-2].lower() not in suffixes:
                first, last = words[0], words[1]
                non_person = (
                    "ck", "nada", "epr", "gcp", "hfm", "manchester", "london", "birmingham",
                    "leeds", "bristol", "liverpool", "urban", "rural", "modern", "green", "city",
                    "associated", "chartered", "registered", "certified", "award", "national",
                    "regional", "contemporary", "bespoke", "creative", "boutique", "innovative",
                    "legal", "commercial", "corporate", "family", "criminal", "premier", "direct"
                )
                has_vowel = any(c in first.lower() for c in "aeiouy")
                if has_vowel and first.lower() not in non_person and last.lower() not in non_person and len(first) > 2:
                    best["first_name"] = first.capitalize()
                    best["name"] = f"{first.capitalize()} {last.capitalize()}"

        return best
