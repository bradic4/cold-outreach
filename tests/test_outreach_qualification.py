from src.outreach.tech_detector import TechDetector
from src.outreach.lead_scorer import LeadScorer


def test_detects_wordpress_elementor_woocommerce():
    html = """
    <link href="/wp-content/plugins/elementor/assets/a.css">
    <div class="elementor-element woocommerce"></div>
    """
    result = TechDetector.detect(html)
    assert result["wordpress"] is True
    assert result["elementor"] is True
    assert result["woocommerce"] is True


def test_score_prioritizes_commercial_wordpress_site():
    score, reasons = LeadScorer.score({
        "reachable": True,
        "wordpress": True,
        "elementor": True,
        "woocommerce": True,
        "commercial_intent": True,
        "scripts": 25,
        "html_bytes": 300000,
        "response_ms": 1700,
        "is_agency": False,
    })
    assert score >= 10
    assert LeadScorer.bucket(score) == "priority"
    assert reasons


def test_agency_penalty():
    score, _ = LeadScorer.score({
        "reachable": True,
        "wordpress": True,
        "elementor": True,
        "commercial_intent": True,
        "scripts": 5,
        "html_bytes": 100000,
        "response_ms": 200,
        "is_agency": True,
    })
    assert score < 4
    assert LeadScorer.bucket(score) == "reject"
