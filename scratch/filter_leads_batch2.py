import json

leads = []
for fname in ['scratch/fresh_leads_3.json', 'scratch/fresh_leads_4.json', 'scratch/fresh_leads_5.json']:
    try:
        with open(fname, encoding='utf-8') as f:
            leads.extend(json.load(f))
    except Exception:
        pass

# Deduplicate by email
unique_leads = {}
for l in leads:
    em = l['email'].lower().strip()
    if em not in unique_leads and 'job' not in em and 'posao' not in em and 'joinus' not in em and 'svjetlost.hr' not in em:
        unique_leads[em] = l

print(f"Total unique leads: {len(unique_leads)}")
for i, (em, l) in enumerate(unique_leads.items(), 1):
    print(f"{i}. {l['name']} -> {em} ({l['url']})")
