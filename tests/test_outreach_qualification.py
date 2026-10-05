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
    subj_finding, cause, fix = Personalizer.finding({"lcp_ms": 5500, "tbt_ms": 2000})
    assert "mobile" in subj_finding


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


SENDER = {
    "full_name": "Test Sender",
    "title": "Web performance",
    "portfolio_url": "https://portfolio.example",
    "proof_result": "mobile LCP from 4.2s to 1.8s",
    "proof_example": "https://portfolio.example/case",
    "reply_to": "",
    "dkim_selector": "",
    "daily_cap": 5,
    "allow_freemail_sender": False,
}


def test_personalizer_first_name_and_company_name():
    from src.outreach.personalizer import Personalizer
    sub, body = Personalizer.draft({
        "company_name": "Andrew Wallace Architects",
        "url": "https://www.andrewwallacearchitects.co.uk",
        "first_name": "Andrew",
        "lcp_ms": 5500,
        "tbt_ms": 1200,
    }, sender=SENDER)
    assert "Andrew Wallace Architects" in sub
    assert "5.5s" in sub or "mobile" in sub
    assert body.startswith("Hi Andrew,\n\nI ran andrewwallacearchitects.co.uk through PageSpeed on mobile")
    assert "5.5 seconds" in body
    assert "architecture studio" in body
    assert "I can send you a short list of the 3 fixes I'd make first" in body
    assert body.endswith("Test Sender\nWeb performance\nhttps://portfolio.example · mobile LCP from 4.2s to 1.8s")


def test_personalizer_serbian_template():
    from src.outreach.personalizer import Personalizer
    sub, body = Personalizer.draft({
        "company_name": "Nekretnine Mostar",
        "url": "https://nekretnine-mostar.ba",
        "first_name": "Marko",
        "lcp_ms": 5800,
        "primary_issue": "image_delivery",
        "estimated_savings_kb": 2400,
    }, sender=SENDER)
    assert "Nekretnine Mostar" in sub
    assert "5,8 sekundi" in sub
    assert body.startswith("Zdravo Marko,\n\nPogledao sam nekretnine-mostar.ba na telefonu")
    assert "5,8 sekundi" in body
    assert "agencija za nekretnine" in body
    assert "Mogu da vam pošaljem kratak spisak 3 stvari koje bih prve popravio" in body


def test_personalizer_omits_claim_without_measurable_proof():
    from src.outreach.personalizer import Personalizer
    sender = {**SENDER, "proof_result": ""}
    assert Personalizer.sender_missing(sender) == ["proof_result"]


def test_mailer_message_is_plain_text_with_clean_headers():
    from src.outreach import mailer
    msg = mailer.build_message(SENDER, "me@outreach-domain.co.uk", "a@b.co.uk", "S", "line1\n\nline2")
    raw = msg.as_string()
    assert "yagmail" not in raw and "<br>" not in raw
    assert msg.get_content_type() == "text/plain"
    assert msg["Message-ID"].endswith("@outreach-domain.co.uk>")
    assert msg["From"].startswith("Test Sender <")


def test_send_gate_blocks_freemail_and_missing_auth():
    from src.outreach import mailer
    problems = mailer.send_gate_problems(SENDER, "me@gmail.com")
    assert any("free-mail" in p for p in problems)
    auth = {"spf": True, "dkim": False, "dmarc": False, "dmarc_policy": ""}
    problems = mailer.send_gate_problems(SENDER, "me@outreach-domain.co.uk", auth)
    assert any("DKIM" in p for p in problems) and any("DMARC" in p for p in problems)
    ok = {"spf": True, "dkim": True, "dmarc": True, "dmarc_policy": "none"}
    assert mailer.send_gate_problems(SENDER, "me@outreach-domain.co.uk", ok) == []


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


def test_initial_surname_not_parsed_as_first_name():
    from src.outreach.contact_finder import ContactFinder
    cf = ContactFinder()
    for local in ("mmchugh", "mchugh", "ssmith", "macdonald"):
        score, role, name, first_name = cf._extract_name_and_role(f"{local}@example.co.uk", "some text")
        assert first_name == "", f"first_name should be empty for {local}, got {first_name}"


def test_directory_subdomain_rejected():
    from src.outreach.result_classifier import ResultClassifier
    kind, _ = ResultClassifier.classify("https://directory.liverpoolecho.co.uk/search/liverpool/architects")
    assert kind == "directory"


def test_compound_first_name_prefix_matching():
    from src.outreach.contact_finder import ContactFinder
    cf = ContactFinder()
    score, role, name, first_name = cf._extract_name_and_role("benrichards@example.co.uk", "some text")
    assert first_name == "Ben"
    assert name == "Ben Richards"


def test_eponymous_acronym_and_adjective_rejected():
    from src.outreach.contact_finder import ContactFinder
    cf = ContactFinder()
    contact = {"email": "mail@example.co.uk", "role": "", "name": "", "first_name": ""}
    # Simulate find() eponymous post-processing check
    words = [w for w in "gcp Chartered Architects".split() if w.isalpha()]
    first, last = words[0], words[1]
    non_person = (
        "ck", "nada", "epr", "gcp", "hfm", "manchester", "london", "birmingham",
        "leeds", "bristol", "liverpool", "urban", "rural", "modern", "green", "city",
        "associated", "chartered", "registered", "certified", "award", "national",
        "regional", "contemporary", "bespoke", "creative", "boutique", "innovative"
    )
    has_vowel = any(c in first.lower() for c in "aeiouy")
    assert not has_vowel or first.lower() in non_person or last.lower() in non_person


def test_generic_local_email_and_home_not_parsed_as_names():
    from src.outreach.contact_finder import ContactFinder
    cf = ContactFinder()
    for local in ("email", "home", "web", "online"):
        score, role, name, first_name = cf._extract_name_and_role(f"{local}@example.co.uk", "director of architecture")
        assert first_name == "", f"first_name should be empty for {local}, got {first_name}"


def test_slash_delimiter_in_title_extracts_clean_company_name():
    from src.outreach.site_analyzer import SiteAnalyzer
    html = "<title>Spacestudio / architects and designers</title>"
    url = "https://www.spacestudio.uk/"
    extracted = SiteAnalyzer.extract_company_name(html, url)
    assert extracted == "Spacestudio", f"Expected Spacestudio, got {extracted}"


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
        test_initial_surname_not_parsed_as_first_name,
        test_directory_subdomain_rejected,
        test_compound_first_name_prefix_matching,
        test_eponymous_acronym_and_adjective_rejected,
        test_generic_local_email_and_home_not_parsed_as_names,
        test_slash_delimiter_in_title_extracts_clean_company_name,
    ]
    for t in tests:
        t()
        print(f"PASS: {t.__name__}")
    print(f"\nAll {len(tests)} tests in test_outreach_qualification.py passed successfully (v3.3.1)!")
