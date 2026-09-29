"""Safe qualification pipeline. Discovery -> cheap screening -> Lighthouse gate. Never sends email."""
import argparse
import csv
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(__file__))

from classes.Outreach import Outreach
from config import ROOT_DIR, get_google_maps_scraper_niche, get_outreach_qualification_config
from outreach.lead_scorer import LeadScorer
from outreach.lighthouse_analyzer import LighthouseAnalyzer
from outreach.result_classifier import ResultClassifier
from outreach.site_analyzer import SiteAnalyzer
from outreach.contact_finder import ContactFinder
from outreach.personalizer import Personalizer


def final_status(row: dict) -> str:
    if row.get("bucket") not in {"qualified", "priority"}:
        return "not_qualified"
    if not row.get("lighthouse_ok"):
        return "needs_lighthouse"
    transfer_kb = row.get("transfer_kb") or 0
    lcp = row.get("lcp_ms") or 0
    if (isinstance(transfer_kb, (int, float)) and transfer_kb > 25000) or (isinstance(lcp, (int, float)) and lcp > 20000):
        return "anomaly_review"
    score = row.get("lighthouse_score")
    tbt = row.get("tbt_ms", 0)
    if (isinstance(score, int) and score <= 60) or lcp >= 4000 or tbt >= 600:
        return "outreach_ready"
    if (isinstance(score, int) and score <= 75) or lcp >= 2500 or tbt >= 300:
        return "review"
    return "performance_good"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--query")
    p.add_argument("--limit", type=int)
    p.add_argument("--region")
    p.add_argument("--skip-lighthouse", action="store_true")
    args = p.parse_args()

    settings = get_outreach_qualification_config()
    query = args.query or get_google_maps_scraper_niche()
    limit = args.limit or settings["analyze_limit"]
    region = args.region or settings["search_region"]
    if not query:
        raise SystemExit("Use --query or configure google_maps_scraper_niche.")

    websites = Outreach().search_business_websites(query, limit=limit, region=region)
    analyzer, lighthouse, contacts = SiteAnalyzer(), LighthouseAnalyzer(), ContactFinder()
    rows = []

    for website in websites:
        result_type, class_reason = ResultClassifier.classify(website)
        if result_type in {"directory", "editorial"}:
            signals = {"url": website, "reachable": True, "result_type": result_type}
        else:
            signals = analyzer.analyze(website)
            signals["result_type"] = result_type

        business, br = LeadScorer.business_score(signals)
        technical, tr = LeadScorer.technical_score(signals)
        score, reasons = LeadScorer.score(signals)
        bucket = LeadScorer.bucket(score, settings["qualified_threshold"], settings["priority_threshold"])
        row = {**signals, "business_score": business, "technical_score": technical,
               "score": score, "bucket": bucket,
               "reasons": "; ".join(([class_reason] if class_reason else []) + reasons)}

        if bucket in {"qualified", "priority"} and not args.skip_lighthouse:
            row.update(lighthouse.analyze_median(row["url"], runs=3))
        row["final_status"] = final_status(row)
        if row["final_status"] == "outreach_ready" and row.get("enterprise_signal") and row.get("internal_marketing_it"):
            row["final_status"] = "enterprise_review"
        rows.append(row)

    rows.sort(key=lambda x: (x.get("final_status") == "outreach_ready", x.get("score", 0)), reverse=True)
    out_dir = os.path.join(ROOT_DIR, "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "qualified.csv")
    fields = ["company_name","url","result_type","bucket","score","business_score","technical_score","final_status",
              "lighthouse_ok","lighthouse_score","lcp_ms","tbt_ms","cls","fcp_ms","speed_index_ms",
              "transfer_kb","requests","primary_issue","estimated_savings_kb","estimated_savings_ms",
              "wordpress","elementor","woocommerce","commercial_intent","conversion_intent",
              "business_identity","team_signal","enterprise_signal","internal_marketing_it","is_agency",
              "response_ms","html_bytes","scripts","stylesheets","images","gtm","meta_pixel","hotjar",
              "clarity","reachable","status_code","reasons"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

    queue_path = os.path.join(out_dir, "outreach_queue.csv")
    history_file = os.path.join(ROOT_DIR, ".mp", "sent_emails_history.txt")
    sent_history = set()
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as hf:
            sent_history = {line.strip().lower() for line in hf if line.strip()}

    queue_rows = []
    for row in rows:
        if row.get("final_status") != "outreach_ready":
            continue
        domain = row["url"].split("//")[-1].split("/")[0].replace("www.", "").strip().lower()
        if domain in sent_history:
            continue
        company = row.get("company_name") or row["url"].split("//")[-1].split("/")[0].replace("www.", "")
        contact = contacts.find(row["url"], company_name=company)
        if not contact.get("email"):
            continue
        if contact["email"].strip().lower() in sent_history:
            continue
        draft_row = {**row, **contact, "company": company, "company_name": company}
        subject, message = Personalizer.draft(draft_row)
        queue_rows.append({
            "company": company, "url": row["url"], "contact_name": contact.get("name", ""),
            "first_name": contact.get("first_name", ""), "email": contact["email"],
            "role": contact.get("role",""), "contact_confidence": contact.get("contact_confidence",""),
            "business_score": row.get("business_score",""), "technical_score": row.get("technical_score",""),
            "lighthouse_score": row.get("lighthouse_score",""), "lcp_ms": row.get("lcp_ms",""),
            "tbt_ms": row.get("tbt_ms",""), "transfer_kb": row.get("transfer_kb",""),
            "primary_issue": row.get("primary_issue",""),
            "subject": subject, "message": message, "status": "ready",
        })
    if queue_rows:
        with open(queue_path, "w", newline="", encoding="utf-8") as f:
            qw = csv.DictWriter(f, fieldnames=list(queue_rows[0].keys()))
            qw.writeheader(); qw.writerows(queue_rows)

    print(f"Analyzed {len(rows)} leads. No email was sent.")
    print(f"Results: {out_path}")
    for row in rows[:10]:
        comp_display = (row.get("company_name") or "")[:25]
        print(f'{row["score"]:>2} {row["bucket"]:<9} {row["final_status"]:<16} {comp_display:<26} {row["url"]}')


if __name__ == "__main__":
    main()
