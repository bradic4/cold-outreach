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

    @classmethod
    def draft(cls, row):
        import html

        company = html.unescape(
            row.get("company_name")
            or row.get("company")
            or row.get("url", "").split("//")[-1].split("/")[0].replace("www.", "")
        )
        first_name = (row.get("first_name") or "").strip()
        if len(first_name) <= 1:
            first_name = ""

        target = f"{company} {row.get('url', '')}".lower()
        if any(k in target for k in ("architect", "architecture")):
            industry = "architecture studio"
        else:
            industry = "law firm"

        greeting = f"Hi {first_name}," if first_name else "Hi,"
        subject = f"{company} site speed"
        body = (
            f"{greeting}\n\n"
            f"I had a look at the {company} website and found a few things that may be making it "
            "slower than it needs to be, especially on mobile.\n\n"
            f"I recently worked on a similar issue for another {industry} and made their "
            "site noticeably faster without changing the design or adding more plugins.\n\n"
            "I noted what I'd look at first on your site too. Want me to send it over?\n\n"
            "Ivan"
        )
        return subject, body
