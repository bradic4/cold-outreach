import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.outreach.tech_detector import TechDetector
from src.outreach.lead_scorer import LeadScorer
from src.outreach.result_classifier import ResultClassifier
from src.qualify_outreach import final_status


def test_detects_stack():
    r = TechDetector.detect('<link href="/wp-content/plugins/elementor/a.css"><div class="woocommerce"></div>')
    assert r["wordpress"] and r["elementor"] and r["woocommerce"]


def test_split_score():
    s={"reachable":True,"result_type":"unknown","wordpress":True,"elementor":True,"commercial_intent":True,
       "conversion_intent":True,"business_identity":True,"team_signal":True,"scripts":25,
       "html_bytes":300000,"response_ms":1700}
    b,_=LeadScorer.business_score(s); t,_=LeadScorer.technical_score(s)
    assert b == 8 and t == 5 and LeadScorer.score(s)[0] == 13


def test_directory_rejected():
    kind,_=ResultClassifier.classify("https://www.houzz.co.uk/professionals/architects/c/Manchester")
    assert kind == "directory"
    assert LeadScorer.score({"reachable":True,"result_type":kind})[0] == 0


def test_enterprise_penalty():
    b,_=LeadScorer.business_score({"reachable":True,"result_type":"unknown","commercial_intent":True,
        "conversion_intent":True,"business_identity":True,"team_signal":True,"enterprise_signal":True,
        "internal_marketing_it":True})
    assert b == 5


def test_lighthouse_gate_marks_bad_performance_ready():
    assert final_status({"bucket":"qualified","lighthouse_ok":True,"lighthouse_score":48,"lcp_ms":5100,"tbt_ms":800}) == "outreach_ready"


def test_lighthouse_gate_rejects_fast_site():
    assert final_status({"bucket":"qualified","lighthouse_ok":True,"lighthouse_score":92,"lcp_ms":1700,"tbt_ms":80}) == "performance_good"


def test_personalizer_uses_measured_performance():
    from src.outreach.personalizer import Personalizer
    text=Personalizer.finding({"lcp_ms":5500,"tbt_ms":2000})
    assert "especially on mobile" in text


def test_contact_role_score_prefers_director():
    from src.outreach.contact_finder import ContactFinder
    high,_=ContactFinder()._score("andrew@example.co.uk","Andrew Wallace Director")
    low,_=ContactFinder()._score("info@example.co.uk","general enquiries")
    assert high > low


def test_lighthouse_anomaly_flag():
    # Extreme transfer_kb (e.g. 143 MB EPR)
    assert final_status({"bucket": "qualified", "lighthouse_ok": True, "lighthouse_score": 21, "lcp_ms": 29700, "tbt_ms": 1200, "transfer_kb": 143000}) == "anomaly_review"
    # Extreme LCP > 20000 ms
    assert final_status({"bucket": "qualified", "lighthouse_ok": True, "lighthouse_score": 30, "lcp_ms": 25000, "tbt_ms": 200, "transfer_kb": 3000}) == "anomaly_review"


def test_generic_email_not_elevated_by_nearby_keywords():
    from src.outreach.contact_finder import ContactFinder
    score, role = ContactFinder()._score("london@epr.co.uk", "Our London marketing and communications team handles press.")
    assert role != "marketing"
    assert role in ("london", "general")


def test_personalizer_first_name_and_company_name():
    from src.outreach.personalizer import Personalizer
    sub, body = Personalizer.draft({
        "company_name": "Andrew Wallace Architects",
        "first_name": "Andrew",
        "lcp_ms": 5500,
        "tbt_ms": 1200,
    })
    assert sub == "Andrew Wallace Architects site speed"
    assert body.startswith("Hi Andrew,\n\nI had a look at the Andrew Wallace Architects website")
    assert "slower than it needs to be, especially on mobile" in body
    assert "without changing the design or adding more plugins" in body
    assert body.endswith("Want me to send it over?\n\nIvan")


def test_site_analyzer_extract_company_name():
    from src.outreach.site_analyzer import SiteAnalyzer
    html = "<title>Andrew Wallace Architects | Architects Manchester</title>"
    url = "https://www.andrewwallacearchitects.co.uk"
    extracted = SiteAnalyzer.extract_company_name(html, url)
    assert extracted == "Andrew Wallace Architects"


def test_image_asset_not_treated_as_email():
    from src.outreach.contact_finder import ContactFinder
    cf = ContactFinder()
    assert "png" in cf.BAD_TLDS
    # Verify that image patterns are excluded
    sample_text = '<img src="/assets/arrow-left-big@2x.png" alt="arrow">'
    found = [m.group(0).lower().strip() for m in cf.EMAIL_RE.finditer(sample_text)]
    valid = [e for e in found if e.split(".")[-1] not in cf.BAD_TLDS and "@2x" not in e]
    assert len(valid) == 0


def test_generic_local_welcome_and_cities_not_parsed_as_names():
    from src.outreach.contact_finder import ContactFinder
    cf = ContactFinder()
    for local in ("welcome", "aberdeen", "birmingham", "leeds", "info"):
        score, role, name, first_name = cf._extract_name_and_role(f"{local}@example.co.uk", "some text")
        assert first_name == "", f"first_name should be empty for {local}, got {first_name}"
        assert name == "", f"name should be empty for {local}, got {name}"


def test_site_analyzer_extracts_acronym_and_filters_generic_descriptors():
    from src.outreach.site_analyzer import SiteAnalyzer
    html = "<title>Architecture Office | Leeds | Halliday Fraser Munro</title>"
    url = "https://www.hfm.co.uk/contact/leeds/"
    extracted = SiteAnalyzer.extract_company_name(html, url)
    assert extracted == "Halliday Fraser Munro", f"Expected Halliday Fraser Munro, got {extracted}"


if __name__ == "__main__":
    tests = [
        test_detects_stack,
        test_split_score,
        test_directory_rejected,
        test_enterprise_penalty,
        test_lighthouse_gate_marks_bad_performance_ready,
        test_lighthouse_gate_rejects_fast_site,
        test_personalizer_uses_measured_performance,
        test_contact_role_score_prefers_director,
        test_lighthouse_anomaly_flag,
        test_generic_email_not_elevated_by_nearby_keywords,
        test_personalizer_first_name_and_company_name,
        test_site_analyzer_extract_company_name,
        test_image_asset_not_treated_as_email,
        test_generic_local_welcome_and_cities_not_parsed_as_names,
        test_site_analyzer_extracts_acronym_and_filters_generic_descriptors,
    ]
    for t in tests:
        t()
        print(f"PASS: {t.__name__}")
    print(f"\nAll {len(tests)} tests in test_outreach_qualification.py passed successfully (v3.3.1)!")
