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
