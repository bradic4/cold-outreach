import re
from urllib.parse import urljoin, urlparse
import requests


class ContactFinder:
    EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    PAGES = ("", "/contact", "/contact-us", "/about", "/about-us", "/team", "/people")
    BAD = ("example.com", "sentry.io", "wixpress.com", "wordpress.org", "elementor.com")
    ROLE_SCORES = {"director":100,"owner":100,"founder":100,"partner":95,"principal":95,
                   "marketing":75,"business":70,"sales":65,"office":50,"info":40,"hello":40,"support":20}

    def __init__(self, timeout=8):
        self.timeout=timeout
        self.headers={"User-Agent":"Mozilla/5.0 (compatible; OutreachQualification/3.3)"}

    def _score(self,email,text):
        local=email.split("@")[0].lower()
        score=55 if "." in local else 35
        role=""
        around=text.lower()
        for key,points in self.ROLE_SCORES.items():
            if key in local or key in around:
                if points>score: score,role=points,key
        return score,role

    def find(self,url):
        candidates={}
        for suffix in self.PAGES:
            page=url if not suffix else urljoin(url,suffix)
            try:
                r=requests.get(page,headers=self.headers,timeout=self.timeout,verify=False)
                if r.status_code!=200: continue
                for m in self.EMAIL_RE.finditer(r.text):
                    email=m.group(0).lower().strip()
                    if any(x in email for x in self.BAD): continue
                    context=re.sub(r"<[^>]+>"," ",r.text[max(0,m.start()-250):m.end()+250])
                    score,role=self._score(email,context)
                    old=candidates.get(email)
                    if not old or score>old["contact_score"]:
                        candidates[email]={"email":email,"role":role,"source_url":page,"contact_score":score}
            except requests.RequestException:
                continue
        if not candidates:
            return {"email":"","role":"","source_url":"","contact_score":0,"contact_confidence":"none"}
        best=max(candidates.values(),key=lambda x:x["contact_score"])
        best["contact_confidence"]="high" if best["contact_score"]>=75 else "medium" if best["contact_score"]>=50 else "low"
        return best
