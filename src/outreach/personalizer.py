class Personalizer:
    @staticmethod
    def finding(row):
        """Keep measured performance evidence available for review/follow-up copy."""
        lcp = int(float(row.get("lcp_ms") or 0))
        tbt = int(float(row.get("tbt_ms") or 0))
        if lcp >= 4000 and tbt >= 1000:
            return "the site is slower than it needs to be, especially on mobile"
        if tbt >= 1000:
            return "the site appears to be doing more work than it needs to, especially on mobile"
        if lcp >= 4000:
            return "the site is taking longer than it should to show its main content, especially on mobile"
        return "there are a few things that may be slowing the site down, especially on mobile"

    @staticmethod
    def sender_missing(sender):
        """Return the config keys that must be set before any email is sent."""
        required = ("full_name", "portfolio_url", "proof_result", "proof_example")
        return [key for key in required if not (sender.get(key) or "").strip()]

    @staticmethod
    def signature(sender):
        lines = [sender["full_name"]]
        if sender.get("title"):
            lines.append(sender["title"])
        if sender.get("portfolio_url"):
            lines.append(f"Portfolio: {sender['portfolio_url']}")
        if sender.get("proof_example"):
            lines.append(f"Example: {sender['proof_example']}")
        return "\n".join(lines)

    @classmethod
    def draft(cls, row, sender=None):
        import html

        if sender is None:
            try:
                from config import get_outreach_sender_config
            except ImportError:
                from src.config import get_outreach_sender_config
            sender = get_outreach_sender_config()

        company = html.unescape(
            row.get("company_name")
            or row.get("company")
            or row.get("url", "").split("//")[-1].split("/")[0].replace("www.", "")
        )
        first_name = (row.get("first_name") or "").strip()
        if len(first_name) <= 1:
            first_name = ""

        greeting = f"Hi {first_name}," if first_name else "Hi,"
        subject = f"{company} site speed"

        paragraphs = [
            greeting,
            f"I had a look at the {company} website and found a few things that may be making it "
            "slower than it needs to be, especially on mobile.",
        ]
        # Only claim what can be measured; an unnamed "worked for another firm" proves nothing.
        if sender.get("proof_result"):
            paragraphs.append(
                f"On a comparable site I recently improved {sender['proof_result']}, "
                "without changing the design or adding more plugins."
            )
        paragraphs.append(
            "I noted what I'd look at first on your site too. Want me to send it over?"
        )
        paragraphs.append(cls.signature(sender))
        return subject, "\n\n".join(paragraphs)
