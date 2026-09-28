class LeadScorer:
    @staticmethod
    def business_score(s: dict) -> tuple[int, list[str]]:
        if not s.get("reachable"):
            return 0, ["unreachable"]
        if s.get("result_type") in {"directory", "editorial"}:
            return 0, [f"excluded {s['result_type']} result"]
        score, reasons = 0, []
        def add(p, r):
            nonlocal score
            score += p
            reasons.append(f"{p:+d} {r}")
        if s.get("commercial_intent"): add(3, "clear commercial service")
        if s.get("conversion_intent"): add(2, "quote/book/contact conversion")
        if s.get("business_identity"): add(2, "business identity signals")
        if s.get("team_signal"): add(1, "team/about signal")
        if s.get("is_agency"): add(-4, "web/digital/SEO agency")
        if s.get("enterprise_signal"): add(-2, "large/enterprise signal")
        if s.get("internal_marketing_it"): add(-1, "internal marketing/IT signal")
        return max(score, 0), reasons

    @staticmethod
    def technical_score(s: dict) -> tuple[int, list[str]]:
        if not s.get("reachable"):
            return 0, ["unreachable"]
        score, reasons = 0, []
        def add(p, r):
            nonlocal score
            score += p
            reasons.append(f"{p:+d} {r}")
        if s.get("wordpress"): add(1, "WordPress")
        if s.get("elementor"): add(1, "Elementor")
        if s.get("scripts", 0) >= 20: add(1, "20+ scripts")
        if s.get("html_bytes", 0) >= 250_000: add(1, "large HTML document")
        if s.get("response_ms", 0) >= 800: add(1, "elevated server response")
        return min(score, 5), reasons

    @classmethod
    def score(cls, s: dict) -> tuple[int, list[str]]:
        b, br = cls.business_score(s)
        t, tr = cls.technical_score(s)
        if s.get("result_type") in {"directory", "editorial"}:
            return 0, br
        return b + t, br + tr

    @staticmethod
    def bucket(score: int, qualified_threshold: int = 7, priority_threshold: int = 10) -> str:
        if score >= priority_threshold: return "priority"
        if score >= qualified_threshold: return "qualified"
        if score >= 4: return "maybe"
        return "reject"
