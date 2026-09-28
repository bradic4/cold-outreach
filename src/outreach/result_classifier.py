import re
from urllib.parse import urlparse


class ResultClassifier:
    """Classify discovery results before spending analysis budget on them."""

    BLOCKED_DOMAINS = {
        "houzz.com", "houzz.co.uk", "clutch.co", "near.co.uk", "yell.com",
        "checkatrade.com", "trustpilot.com", "linkedin.com", "facebook.com",
        "instagram.com", "pinterest.com", "wikipedia.org", "grokipedia.com",
        "find-my-architect.com",
    }
    EDITORIAL_DOMAINS = {"e-architect.com", "re-thinkingthefuture.com"}
    DIRECTORY_PATH_PATTERNS = (
        r"/professionals?/", r"/directory(?:/|$)", r"/best-", r"/top-",
        r"/architects?-in-", r"/find-", r"/probr\d",
    )

    @staticmethod
    def _root_domain(hostname: str) -> str:
        host = (hostname or "").lower().split(":")[0]
        if host.startswith("www."):
            host = host[4:]
        return host

    @classmethod
    def classify(cls, url: str) -> tuple[str, str]:
        parsed = urlparse(url)
        host = cls._root_domain(parsed.hostname or "")
        path = (parsed.path or "/").lower()

        if any(host == domain or host.endswith("." + domain) for domain in cls.BLOCKED_DOMAINS):
            return "directory", f"known directory/marketplace: {host}"
        if any(host == domain or host.endswith("." + domain) for domain in cls.EDITORIAL_DOMAINS):
            return "editorial", f"known editorial site: {host}"
        if any(re.search(pattern, path) for pattern in cls.DIRECTORY_PATH_PATTERNS):
            return "directory", f"directory/listicle path: {path}"
        return "unknown", ""
