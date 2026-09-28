import time
from urllib.parse import urljoin, urlparse

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
            response = requests.get(url, headers=self.headers, timeout=self.timeout, verify=False, allow_redirects=True)
            elapsed_ms = round((time.perf_counter() - started) * 1000)
            html = response.text if response.ok else ""
        except requests.RequestException as exc:
            return {"url": url, "reachable": False, "error": str(exc), "score": 0}

        lower = html.lower()
        tech = TechDetector.detect(html)
        result = {
            "url": response.url,
            "reachable": response.ok,
            "status_code": response.status_code,
            "response_ms": elapsed_ms,
            "html_bytes": len(response.content),
            "scripts": len(re.findall(r"<script\\b", lower)),
            "stylesheets": len(re.findall(r"<link\\b[^>]*rel=[\\\"']?stylesheet", lower)),
            "images": len(re.findall(r"<img\\b", lower)),
            "commercial_intent": any(x in lower for x in ("request a quote", "get a quote", "book a consultation", "contact us", "our services", "our projects")),
            "is_agency": any(x in lower for x in ("web design agency", "digital agency", "seo agency", "marketing agency")),
            **tech,
        }
        return result


# local import kept here to make the module easy to unit test/mocking-friendly
import re
