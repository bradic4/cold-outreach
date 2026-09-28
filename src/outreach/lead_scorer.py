class LeadScorer:
    """Deterministic first-pass scoring. Thresholds are intentionally easy to tune."""

    @staticmethod
    def score(signals: dict) -> tuple[int, list[str]]:
        score = 0
        reasons = []

        def add(points, reason):
            nonlocal score
            score += points
            reasons.append(f"{points:+d} {reason}")

        if not signals.get("reachable"):
            return 0, ["unreachable"]
        if signals.get("wordpress"):
            add(1, "WordPress")
        if signals.get("elementor"):
            add(2, "Elementor")
        if signals.get("woocommerce"):
            add(1, "WooCommerce")
        if signals.get("commercial_intent"):
            add(2, "commercial intent")
        if signals.get("scripts", 0) >= 20:
            add(2, "20+ scripts")
        elif signals.get("scripts", 0) >= 12:
            add(1, "12+ scripts")
        if signals.get("html_bytes", 0) >= 250_000:
            add(1, "large HTML document")
        if signals.get("response_ms", 0) >= 1500:
            add(2, "slow server response")
        elif signals.get("response_ms", 0) >= 800:
            add(1, "elevated server response")
        if signals.get("is_agency"):
            add(-4, "web/digital/SEO agency")

        return max(score, 0), reasons

    @staticmethod
    def bucket(score: int, qualified_threshold: int = 7, priority_threshold: int = 10) -> str:
        if score >= priority_threshold:
            return "priority"
        if score >= qualified_threshold:
            return "qualified"
        if score >= 4:
            return "maybe"
        return "reject"
