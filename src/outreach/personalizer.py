class Personalizer:
    @staticmethod
    def finding(row):
        lcp=int(float(row.get("lcp_ms") or 0)); tbt=int(float(row.get("tbt_ms") or 0))
        if lcp>=4000 and tbt>=1000:
            return "the mobile site is doing a lot of work before the main content becomes responsive"
        if tbt>=1000:
            return "the mobile site is spending a significant amount of time processing JavaScript"
        if lcp>=4000:
            return "the main content on mobile is appearing quite late"
        return "there appear to be a few mobile performance bottlenecks worth investigating"

    @classmethod
    def draft(cls, row):
        company = row.get("company_name") or row.get("company") or row.get("url", "").split("//")[-1].split("/")[0].replace("www.", "")
        first_name = (row.get("first_name") or "").strip()
        greeting = f"Hi {first_name}," if first_name else "Hi,"
        subject = f"Quick question about {company}"
        body = (f"{greeting}\n\nI came across {company} and noticed {cls.finding(row)}.\n\n"
              "I recently worked on a similar WordPress site where I reduced mobile page weight by 54% "
              "and improved LCP from 5.08s to 3.49s without adding another optimization plugin.\n\n"
              "I found a couple of things I'd investigate first. Happy to send them over if useful.\n\nIvan")
        return subject, body
