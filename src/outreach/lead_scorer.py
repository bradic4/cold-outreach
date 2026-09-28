class LeadScorer:
    """Separate commercial fit from cheap technical screening."""

    @staticmethod
    def business_score(signals: dict) -> tuple[int, list[str]]:
        score, reasons = 0, []

        def add(points, reason):
            nonlocal score
            score += points
            reasons.append(f"{points:+d} {reason}")

        if not signals.get("reachable"):
            return 0, ["unreachable"]
        if signals.get("result_type") in {"directory", "editorial"}:
            return 0, [f"excluded {signals['result_type']} result"]
        if signals.get("commercial_intent"):
            add(3, "clear commercial service")
        if signals.get("conversion_intent"):
            add(2, "quote/book/contact conversion")
        if signals.get("business_identity"):
            add(2, "business identity signals")
        if signals.get("team_signal"):
            add(1, "team/about signal")
        if signals.get("is_agency"):
            add(-4, "web/digital/SEO agency")
        if signals.get("enterprise_signal"):
            add(-2, "large/enterprise signal")
        if signals.get("internal_marketing_it"):
            add(-1, "internal marketing/IT signal")
        return max(score, 0), reasons

    @staticmethod
    def technical_score(signals: dict) -> tuple[int, list[str]]:
        score, reasons = 0, []

        def add(points, reason):
            nonlocal score
            score += points
            reasons.append(f"{points:+d} {reason}")

        if not signals.get("reachable"):
            return 0, ["unreachable"]
        if signals.get("wordpress"):
            add(1, "WordPress")
        if signals.get("elementor"):
            add(1, "Elementor")
        if signals.get("scripts", 0) >= 20:
            add(1, "20+ scripts")
        if signals.get("html_bytes", 0) >= 250_000:
            add(1, "large HTML document")
        if signals.get("response_ms", 0) >= 800:
            add(1, "elevated server response")
        return min(score, 5), reasons

    @classmethod
    def score(cls, signals: dict) -> tuple[int, list[str]]:
        business, business_reasons = cls.business_score(signals)
        technical, technical_reasons = cls.technical_score(signals)
        if signals.get("result_type") in {"directory", "editorial"}:
            return 0, business_reasons
        return business + technical, business_reasons + technical_reasons

    @staticmethod
    def bucket(score: int, qualified_threshold: int = 7, priority_threshold: int = 10) -> str:
        if score >= priority_threshold:
            return "priority"
        if score >= qualified_threshold:
            return "qualified"
        if score >= 4:
            return "maybe"
        return "reject"
