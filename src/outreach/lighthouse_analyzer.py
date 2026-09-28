import json
import os
import shutil
import subprocess
import tempfile


class LighthouseAnalyzer:
    """Run local Lighthouse only after cheap qualification has passed."""

    def __init__(self, timeout: int = 120):
        self.timeout = timeout

    @staticmethod
    def available() -> bool:
        return bool(shutil.which("npx"))

    def analyze(self, url: str) -> dict:
        if not self.available():
            return {"lighthouse_ok": False, "lighthouse_error": "npx not found"}

        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            cmd = [
                "npx", "--yes", "lighthouse", url,
                "--quiet", "--chrome-flags=--headless --no-sandbox",
                "--only-categories=performance", "--output=json",
                f"--output-path={path}",
            ]
            subprocess.run(cmd, check=True, timeout=self.timeout, capture_output=True, text=True)
            with open(path, "r", encoding="utf-8") as f:
                report = json.load(f)

            audits = report.get("audits", {})
            perf = report.get("categories", {}).get("performance", {}).get("score")
            value = lambda key: audits.get(key, {}).get("numericValue")
            details = lambda key: audits.get(key, {}).get("details", {}).get("overallSavingsBytes", 0) or 0

            opportunities = {
                "image_delivery": details("modern-image-formats") + details("uses-responsive-images") + details("uses-optimized-images"),
                "unused_javascript": details("unused-javascript"),
                "render_blocking": audits.get("render-blocking-resources", {}).get("details", {}).get("overallSavingsMs", 0) or 0,
            }
            primary = max(opportunities, key=opportunities.get) if any(opportunities.values()) else ""

            return {
                "lighthouse_ok": True,
                "lighthouse_score": round(perf * 100) if perf is not None else "",
                "lcp_ms": round(value("largest-contentful-paint") or 0),
                "tbt_ms": round(value("total-blocking-time") or 0),
                "cls": round(value("cumulative-layout-shift") or 0, 3),
                "fcp_ms": round(value("first-contentful-paint") or 0),
                "speed_index_ms": round(value("speed-index") or 0),
                "transfer_kb": round((value("total-byte-weight") or 0) / 1024),
                "requests": len(audits.get("network-requests", {}).get("details", {}).get("items", [])),
                "primary_issue": primary,
                "estimated_savings_kb": round(opportunities.get(primary, 0) / 1024) if primary and primary != "render_blocking" else "",
                "estimated_savings_ms": round(opportunities.get(primary, 0)) if primary == "render_blocking" else "",
            }
        except (subprocess.SubprocessError, OSError, json.JSONDecodeError) as exc:
            return {"lighthouse_ok": False, "lighthouse_error": str(exc)}
        finally:
            try:
                os.remove(path)
            except OSError:
                pass
