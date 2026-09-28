"""Safe qualification pipeline. Discovery -> cheap screening -> Lighthouse gate. Never sends email."""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from classes.Outreach import Outreach
from config import ROOT_DIR, get_google_maps_scraper_niche, get_outreach_qualification_config
from outreach.lead_scorer import LeadScorer
from outreach.lighthouse_analyzer import LighthouseAnalyzer
from outreach.result_classifier import ResultClassifier
from outreach.site_analyzer import SiteAnalyzer


def final_status(row: dict) -> str:
    if row.get("bucket") not in {"qualified", "priority"}:
        return "not_qualified"
    if not row.get("lighthouse_ok"):
        return "needs_lighthouse"
    score = row.get("lighthouse_score")
    lcp = row.get("lcp_ms", 0)
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
    analyzer, lighthouse = SiteAnalyzer(), LighthouseAnalyzer()
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
            row.update(lighthouse.analyze(row["url"]))
        row["final_status"] = final_status(row)
        rows.append(row)

    rows.sort(key=lambda x: (x.get("final_status") == "outreach_ready", x.get("score", 0)), reverse=True)
    out_dir = os.path.join(ROOT_DIR, "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "qualified.csv")
    fields = ["url","result_type","bucket","score","business_score","technical_score","final_status",
              "lighthouse_ok","lighthouse_score","lcp_ms","tbt_ms","cls","fcp_ms","speed_index_ms",
              "transfer_kb","requests","primary_issue","estimated_savings_kb","estimated_savings_ms",
              "wordpress","elementor","woocommerce","commercial_intent","conversion_intent",
              "business_identity","team_signal","enterprise_signal","internal_marketing_it","is_agency",
              "response_ms","html_bytes","scripts","stylesheets","images","gtm","meta_pixel","hotjar",
              "clarity","reachable","status_code","reasons"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

    print(f"Analyzed {len(rows)} leads. No email was sent.")
    print(f"Results: {out_path}")
    for row in rows[:10]:
        print(f'{row["score"]:>2} {row["bucket"]:<9} {row["final_status"]:<16} {row["url"]}')


if __name__ == "__main__":
    main()
