import re
from urllib.parse import urlparse


class ResultClassifier:
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

    @classmethod
    def classify(cls, url: str) -> tuple[str, str]:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower().removeprefix("www.")
        path = (parsed.path or "/").lower()
        if any(host == d or host.endswith("." + d) for d in cls.BLOCKED_DOMAINS):
            return "directory", f"known directory/marketplace: {host}"
        if any(host == d or host.endswith("." + d) for d in cls.EDITORIAL_DOMAINS):
            return "editorial", f"known editorial site: {host}"
        if any(re.search(pattern, path) for pattern in cls.DIRECTORY_PATH_PATTERNS):
            return "directory", f"directory/listicle path: {path}"
        return "unknown", ""
