import json

with open('scratch/fresh_leads.json', encoding='utf-8') as f:
    l1 = json.load(f)
with open('scratch/fresh_leads_2.json', encoding='utf-8') as f:
    l2 = json.load(f)

all_leads = l1 + l2
print(f"Total: {len(all_leads)}")
for i, l in enumerate(all_leads, 1):
    print(f"{i}. {l['name']} -> {l['email']} ({l['url']})")
