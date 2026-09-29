import json
import os
import shutil
import subprocess
import tempfile
import statistics


class LighthouseAnalyzer:
    """Run local Lighthouse only after cheap qualification has passed."""

    def __init__(self, timeout: int = 120):
        self.timeout = timeout

    @staticmethod
    def available() -> bool:
        return bool(shutil.which("npx"))

    def analyze(self, url: str) -> dict:
        npx_bin = shutil.which("npx") or "npx"
        if not self.available():
            return {"lighthouse_ok": False, "lighthouse_error": "npx not found"}

        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            cmd = [
                npx_bin, "--yes", "lighthouse", url,
                "--quiet", "--chrome-flags=--headless --no-sandbox",
                "--only-categories=performance", "--output=json",
                f"--output-path={path}",
            ]
            proc = subprocess.run(
                cmd,
                check=False,
                timeout=self.timeout,
                capture_output=True,
                text=True,
                shell=(os.name == "nt"),
            )
            if not os.path.exists(path) or os.path.getsize(path) == 0:
                err_msg = (proc.stderr or "").strip() or f"exit status {proc.returncode}"
                return {"lighthouse_ok": False, "lighthouse_error": err_msg}

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


    def analyze_median(self, url: str, runs: int = 3) -> dict:
        results = [self.analyze(url) for _ in range(runs)]
        good = [r for r in results if r.get("lighthouse_ok")]
        if not good:
            return results[-1] if results else {"lighthouse_ok": False, "lighthouse_error": "no runs"}
        numeric = ("lighthouse_score","lcp_ms","tbt_ms","cls","fcp_ms","speed_index_ms","transfer_kb","requests")
        out = {"lighthouse_ok": True, "lighthouse_runs": len(good)}
        for key in numeric:
            vals=[r[key] for r in good if isinstance(r.get(key),(int,float))]
            out[key]=round(statistics.median(vals),3) if vals else ""
        issues=[r.get("primary_issue") for r in good if r.get("primary_issue")]
        out["primary_issue"]=max(set(issues),key=issues.count) if issues else ""
        scores=[r.get("lighthouse_score") for r in good if isinstance(r.get("lighthouse_score"),(int,float))]
        out["lighthouse_score_spread"]=round(max(scores)-min(scores),1) if scores else ""
        return out
