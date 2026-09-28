from src.outreach.tech_detector import TechDetector
from src.outreach.lead_scorer import LeadScorer
from src.outreach.result_classifier import ResultClassifier


def test_detects_wordpress_elementor_woocommerce():
    html = '<link href="/wp-content/plugins/elementor/a.css"><div class="elementor-element woocommerce"></div>'
    result = TechDetector.detect(html)
    assert result["wordpress"] and result["elementor"] and result["woocommerce"]


def test_split_scoring_prioritizes_good_fit():
    signals = {
        "reachable": True, "result_type": "unknown", "wordpress": True, "elementor": True,
        "commercial_intent": True, "conversion_intent": True, "business_identity": True,
        "team_signal": True, "scripts": 25, "html_bytes": 300000, "response_ms": 1700,
        "is_agency": False, "enterprise_signal": False, "internal_marketing_it": False,
    }
    business, _ = LeadScorer.business_score(signals)
    technical, _ = LeadScorer.technical_score(signals)
    total, _ = LeadScorer.score(signals)
    assert business == 8
    assert technical == 5
    assert total == 13
    assert LeadScorer.bucket(total) == "priority"


def test_technical_score_is_capped_at_five():
    score, _ = LeadScorer.technical_score({
        "reachable": True, "wordpress": True, "elementor": True, "scripts": 99,
        "html_bytes": 999999, "response_ms": 5000,
    })
    assert score == 5


def test_enterprise_and_internal_team_are_penalized():
    business, _ = LeadScorer.business_score({
        "reachable": True, "result_type": "unknown", "commercial_intent": True,
        "conversion_intent": True, "business_identity": True, "team_signal": True,
        "is_agency": False, "enterprise_signal": True, "internal_marketing_it": True,
    })
    assert business == 5


def test_known_directory_is_rejected_before_scoring():
    result_type, reason = ResultClassifier.classify(
        "https://www.houzz.co.uk/professionals/architects-and-building-designers/c/Manchester"
    )
    assert result_type == "directory"
    assert reason
    total, _ = LeadScorer.score({"reachable": True, "result_type": result_type})
    assert total == 0


def test_directory_path_is_detected():
    result_type, _ = ResultClassifier.classify("https://example.com/best-architects-manchester/")
    assert result_type == "directory"


def test_agency_penalty():
    business, _ = LeadScorer.business_score({
        "reachable": True, "result_type": "unknown", "commercial_intent": True,
        "conversion_intent": False, "business_identity": False, "team_signal": False,
        "is_agency": True, "enterprise_signal": False, "internal_marketing_it": False,
    })
    assert business == 0
