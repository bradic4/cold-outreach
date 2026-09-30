import re
import time

import requests

from .tech_detector import TechDetector


class SiteAnalyzer:
    """Cheap HTTP/HTML screening. No browser, Lighthouse, paid API, or LLM required."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; ColdOutreachQualification/3.0)"}

    def analyze(self, url: str) -> dict:
        started = time.perf_counter()
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                verify=False,
                allow_redirects=True,
            )
            elapsed_ms = round((time.perf_counter() - started) * 1000)
            html = response.text if response.ok else ""
        except requests.RequestException as exc:
            return {"url": url, "reachable": False, "error": str(exc), "score": 0}

        lower = html.lower()
        tech = TechDetector.detect(html)
        return {
            "url": response.url,
            "company_name": self.extract_company_name(html, response.url),
            "reachable": response.ok,
            "status_code": response.status_code,
            "response_ms": elapsed_ms,
            "html_bytes": len(response.content),
            "scripts": len(re.findall(r"<script\b", lower)),
            "stylesheets": len(re.findall(r"<link\b[^>]*rel=[\"']?stylesheet", lower)),
            "images": len(re.findall(r"<img\b", lower)),
            "commercial_intent": any(x in lower for x in ("our services", "our projects", "services", "portfolio", "case studies")),
            "conversion_intent": any(x in lower for x in ("request a quote", "get a quote", "book a consultation", "book a call", "contact us", "enquire", "get in touch")),
            "business_identity": any(x in lower for x in ("company number", "registered office", "our studio", "our practice", "our company")),
            "team_signal": any(x in lower for x in ("our team", "meet the team", "our people", "/team", "/people")),
            "enterprise_signal": sum(lower.count(x) for x in ("our offices", "our studios", "locations", "international", "global")) >= 3,
            "internal_marketing_it": any(x in lower for x in ("marketing director", "marketing manager", "head of marketing", "it manager", "head of it", "digital director")),
            "is_agency": any(
                x in lower
                for x in ("web design agency", "digital agency", "seo agency", "marketing agency")
            ),
            **tech,
        }

    @staticmethod
    def extract_company_name(html: str, url: str) -> str:
        domain_stem = url.split("//")[-1].split("/")[0].replace("www.", "").split(".")[0]
        domain_clean = re.sub(r"[^a-z0-9]", "", domain_stem.lower())
        default_name = domain_stem.replace("-", " ").title()
        if not html:
            return default_name

        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
        title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else ""

        candidates = []
        generic_descriptors = {
            "architecture office", "architectural office", "architecture practice",
            "architectural practice", "architectural services", "architecture services",
            "chartered architects", "riba chartered practice", "riba chartered architects",
            "award winning architects", "commercial architects", "residential architects",
            "interior design", "landscape architects", "architecture studio", "design studio",
            "architects and designers", "architectural designers"
        }
        uk_cities = {
            "london", "manchester", "birmingham", "leeds", "bristol", "liverpool",
            "aberdeen", "edinburgh", "glasgow", "cardiff", "belfast", "newcastle",
            "sheffield", "nottingham", "oxford", "cambridge", "york", "bath"
        }
        if title:
            chunks = [c.strip() for c in re.split(r"[\|\—\–\-\•\:\,\/\\]", title) if c.strip()]
            bad_words = ("home", "welcome", "about", "contact", "official site", "residential")
            for chunk in chunks:
                c_lower = chunk.lower().strip()
                if any(b in c_lower for b in bad_words) or len(chunk) < 3 or len(chunk) > 45:
                    continue
                if c_lower in generic_descriptors or any(c_lower.startswith(d) for d in ("award winning", "chartered architects in", "architectural services in", "architecture practice in", "best architects in")):
                    continue
                c_clean = re.sub(r"[^a-z0-9]", "", c_lower)
                score = 1.0
                if c_clean == domain_clean:
                    score += 10.0
                elif c_clean in domain_clean or domain_clean in c_clean:
                    score += 5.0

                # Check for acronym match (e.g. Halliday Fraser Munro -> hfm)
                words = [w for w in re.split(r"\s+", c_lower) if w]
                initials = "".join(w[0] for w in words)
                if len(domain_clean) >= 3 and initials == domain_clean:
                    score += 8.0

                if any(k in c_lower for k in ("architects", "architecture", "studio", "design", "practice")):
                    score += 2.0
                for city in uk_cities:
                    if c_lower in (city, f"architects {city}", f"{city} architects", f"architects in {city}", f"architecture in {city}"):
                        score -= 5.0
                candidates.append((chunk, score))

        ld_matches = re.findall(r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.I | re.S)
        for ld in ld_matches:
            nm = re.search(r'"name"\s*:\s*"([^"]+)"', ld)
            if nm:
                name = nm.group(1).strip()
                if 2 < len(name) < 45 and not any(x in name.lower() for x in ("home", "welcome")) and name.lower() not in generic_descriptors:
                    score = 3.0
                    if re.sub(r"[^a-z0-9]", "", name.lower()) == domain_clean:
                        score += 10.0
                    candidates.append((name, score))

        og_match = re.search(r'<meta\s+[^>]*property=["\']og:site_name["\'][^>]*content=["\']([^"\']+)["\']', html, re.I)
        if not og_match:
            og_match = re.search(r'<meta\s+[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:site_name["\']', html, re.I)
        if og_match:
            og_name = og_match.group(1).strip()
            if 2 < len(og_name) < 45 and not any(x in og_name.lower() for x in ("home", "welcome", "wordpress", "elementor")):
                score = 2.0
                if re.sub(r"[^a-z0-9]", "", og_name.lower()) == domain_clean:
                    score += 10.0
                candidates.append((og_name, score))

        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            import html
            return html.unescape(candidates[0][0])

        import html
        return html.unescape(default_name)
