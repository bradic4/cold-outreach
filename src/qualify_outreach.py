"""Dry-run qualification runner.

Discovers candidates using the existing Outreach search, analyzes them cheaply,
scores them, and persists results. This module never sends email.
"""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from classes.Outreach import Outreach
from config import ROOT_DIR, get_google_maps_scraper_niche, get_outreach_qualification_config
from outreach.site_analyzer import SiteAnalyzer
from outreach.lead_scorer import LeadScorer\nfrom outreach.result_classifier import ResultClassifier


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", help="Override configured niche/search query")
    parser.add_argument("--limit", type=int, help="Maximum candidates to analyze")
    args = parser.parse_args()

    settings = get_outreach_qualification_config()
    query = args.query or get_google_maps_scraper_niche()
    limit = args.limit or settings["analyze_limit"]

    if not query:
        raise SystemExit("No query configured. Use --query or google_maps_scraper_niche.")

    outreach = Outreach()
    websites = outreach.search_business_websites(query, limit=limit, region=settings["search_region"])
    analyzer = SiteAnalyzer()
    rows = []

    for website in websites:
        signals = analyzer.analyze(website)
        score, reasons = LeadScorer.score(signals)
        bucket = LeadScorer.bucket(score, settings["qualified_threshold"], settings["priority_threshold"])
        rows.append({
            **signals,
            "business_score": business_score,
            "technical_score": technical_score,
            "score": score,
            "bucket": bucket,
            "reasons": "; ".join(reasons),
        })

    rows.sort(key=lambda x: x["score"], reverse=True)
    out_dir = os.path.join(ROOT_DIR, "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "qualified.csv")
    fields = ["url", "bucket", "score", "wordpress", "elementor", "woocommerce", "commercial_intent",
              "is_agency", "response_ms", "html_bytes", "scripts", "stylesheets", "images",
              "gtm", "meta_pixel", "hotjar", "clarity", "reachable", "status_code", "reasons"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Analyzed {len(rows)} leads. No email was sent.")
    print(f"Results: {out_path}")
    for row in rows[:10]:
        print(f'{row["score"]:>2} {row["bucket"]:<9} {row["url"]}')


if __name__ == "__main__":
    main()
