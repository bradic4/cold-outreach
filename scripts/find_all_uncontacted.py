import glob
import re
import json
import os

sent = set(open('.mp/sent_emails_history.txt', encoding='utf-8').read().splitlines())
candidates = []

for f in glob.glob('scripts/test_*.py'):
    text = open(f, encoding='utf-8', errors='ignore').read()
    # find dicts
    matches = re.findall(r'\{[^{}]*\}', text)
    for m in matches:
        if 'email' in m and 'url' in m:
            u = re.search(r'[\'\"]url[\'\"]\s*:\s*[\'\"]([^\'\"]+)[\'\"]', m)
            e = re.search(r'[\'\"]email[\'\"]\s*:\s*[\'\"]([^\'\"]+)[\'\"]', m)
            n = re.search(r'[\'\"](?:name|company)[\'\"]\s*:\s*[\'\"]([^\'\"]+)[\'\"]', m)
            ro = re.search(r'[\'\"](?:role|niche)[\'\"]\s*:\s*[\'\"]([^\'\"]+)[\'\"]', m)
            if u and e:
                url = u.group(1).strip()
                email = e.group(1).strip().lower()
                name = n.group(1).strip() if n else ''
                role = ro.group(1).strip() if ro else ''
                dom = url.split('//')[-1].split('/')[0].replace('www.', '').lower()
                if email not in sent and dom not in sent:
                    candidates.append({'company': name, 'url': url, 'email': email, 'role': role})

seen_dom = set()
unique = []
for c in candidates:
    dom = c['url'].split('//')[-1].split('/')[0].replace('www.', '').lower()
    if dom not in seen_dom:
        seen_dom.add(dom)
        unique.append(c)

print(f"FOUND UNCONTACTED CANDIDATES: {len(unique)}")
for c in unique[:15]:
    print(c)

with open('.mp/uncontacted_candidates.json', 'w', encoding='utf-8') as f:
    json.dump(unique, f, indent=2)
