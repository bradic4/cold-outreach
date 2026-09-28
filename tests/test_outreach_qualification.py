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
    assert "responsive" in text


def test_contact_role_score_prefers_director():
    from src.outreach.contact_finder import ContactFinder
    high,_=ContactFinder()._score("andrew@example.co.uk","Andrew Wallace Director")
    low,_=ContactFinder()._score("info@example.co.uk","general enquiries")
    assert high > low
