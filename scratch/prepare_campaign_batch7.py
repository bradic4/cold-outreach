import json

leads_data = [
    # 1. Kancelarijski nameštaj & Opremanje poslovnih prostora (Velike B2B karte)
    {
        "niche": "office_furniture",
        "name": "Modrulj Kancelarijski Nameštaj",
        "email": "office@kancelarijske-stolice.com",
        "url": "https://kancelarijske-stolice.com/",
        "subject": "Pitanje u vezi B2B kataloga i porudzbina na kancelarijske-stolice.com",
        "hook_points": [
            "Mobilni konfigurator stolica i brzi upitnik za opremanje kancelarija u 2 klika.",
            "Ubrzanje ucitavanja masivnog kataloga i filtera na mobilnoj 4G mrezi.",
            "Google rang za kancelarijski namestaj i ergonomske stolice u Srbiji."
        ]
    },
    {
        "niche": "office_furniture",
        "name": "Nitea Kancelarijski Nameštaj",
        "email": "home@nitea.rs",
        "url": "https://nitea.rs/",
        "subject": "Pitanje u vezi prezentacije i B2B opremanja na nitea.rs",
        "hook_points": [
            "Optimizacija premijum dizajnerskih vizuala za trenutno otvaranje na telefonu.",
            "Olakšano slanje projektnih specifikacija za arhitekte i investitore sa mobilnog.",
            "Corporate SEO dominacija za ekskluzivno opremanje radnih prostora."
        ]
    },
    {
        "niche": "office_furniture",
        "name": "Office Pro Nameštaj",
        "email": "info@officepro.rs",
        "url": "https://officepro.rs/",
        "subject": "Pitanje u vezi mobilnog kataloga na officepro.rs",
        "hook_points": [
            "Fiksirano dugme 'Zatrazite ponudu za opremanje kancelarije' na dnu ekrana.",
            "Kompresija slika radnih stolova i pregrada za rad bez zastoja na 4G.",
            "Google pozicioniranje za opremanje poslovnih prostora."
        ]
    },

    # 2. HR Agencije & Regrutacija radnika (Jeseni talas zapošljavanja — HOT niche)
    {
        "niche": "hr_recruitment",
        "name": "HES Regrutacija",
        "email": "info@hes.rs",
        "url": "https://hes.rs/",
        "subject": "Pitanje u vezi B2B upita za zaposljavanje na hes.rs",
        "hook_points": [
            "Mobilna forma za poslodavce: slanje zahteva za profile radnika u 2 klika.",
            "Ubrzanje baze otvorenih konkursa i opisa usluga na mobilnom internetu.",
            "Google SEO rang za agencije za zaposljavanje i regrutaciju kadrova."
        ]
    },
    {
        "niche": "hr_recruitment",
        "name": "Gi Group Srbija",
        "email": "office@gigroup.com",
        "url": "https://gigroup.rs/",
        "subject": "Pitanje u vezi akvizicije poslodavaca na gigroup.rs",
        "hook_points": [
            "Pojednostavljen kontakt za HR direktore i kompanije sa mobilnih telefona.",
            "Smanjenje vremena otvaranja stranica sa B2B HR resursima na 4G.",
            "Corporate Google dominacija za privremeno zaposljavanje i lizing radnika."
        ]
    },
    {
        "niche": "hr_recruitment",
        "name": "Hill International Srbija",
        "email": "office@hill-international.com",
        "url": "https://hill-international.com/",
        "subject": "Pitanje u vezi executive search prezentacije za Hill International",
        "hook_points": [
            "Brzi diskretni upitnik za kompanije koje traze rukovodeci kadar sa telefona.",
            "Optimizacija prikaza regionalne mreze i ekspertize za pametne telefone.",
            "Google rang za executive search i headhunting u Srbiji."
        ]
    },

    # 3. Automatske kapije, ograde & rolo vrata
    {
        "niche": "automatic_gates",
        "name": "Bramont Kapije i Ograde",
        "email": "office@cnc-bube-bramont.com",
        "url": "https://bramont.rs/",
        "subject": "Pitanje u vezi proracuna kapija i ograda na bramont.rs",
        "hook_points": [
            "Mobilni upitnik za dimenzije i izradu CNC kapija u 2 klika sa telefona.",
            "Kompresija fotografija montiranih kapija za rad bez zastoja na 4G.",
            "Lokalni Google SEO za izradu modernih kapija i ograda."
        ]
    },
    {
        "niche": "automatic_gates",
        "name": "Roloplast Mošić",
        "email": "rok.kovacic@roloplastmosic.com",
        "url": "https://roloplastmosic.rs/",
        "subject": "Pitanje u vezi rolo vrata i sistema na roloplastmosic.rs",
        "hook_points": [
            "Taster za brzi proracun cene rolo vrata i komarnika na mobilnom.",
            "Ubrzanje tehnickih kataloga i specifikacija motora za telefone.",
            "Google rang za automatska vrata i roletne u Srbiji."
        ]
    },

    # 4. Dermatologija & Laserski centri (Anti-aging & tretmani)
    {
        "niche": "dermatology",
        "name": "Dermatološka ordinacija Dr Babović",
        "email": "dr.gligorijebabovic@gmail.com",
        "url": "https://drbabovic.com/",
        "subject": "Pitanje u vezi zakazivanja pregleda na drbabovic.com",
        "hook_points": [
            "Mobilno zakazivanje dermatoloskih pregleda i laserskih tretmana u 2 klika.",
            "Ubrzanje ucitavanja stranica sa tretmanima i cenovnikom na 4G mrezi.",
            "Google pozicioniranje za privatnu dermatologiju u Beogradu."
        ]
    },
    {
        "niche": "dermatology",
        "name": "Ordinacija Derma Viva",
        "email": "ordinacijadermaviva@gmail.com",
        "url": "https://dermaviva.rs/",
        "subject": "Pitanje u vezi mobilne verzije sajta dermaviva.rs",
        "hook_points": [
            "Fiksirano dugme 'Zakazite konsultaciju' pri skrolovanju na dnu ekrana.",
            "Optimizacija galerije rezultata tretmana za telefone bez cekanja.",
            "Lokalni Google profil za estetske i medicinske tretmane koze."
        ]
    }
]

with open('.mp/sent_emails_history.txt', 'r', encoding='utf-8', errors='ignore') as f:
    history = set(line.strip().lower() for line in f if line.strip())

verified_batch7 = []
for lead in leads_data:
    if lead['email'].lower() not in history:
        verified_batch7.append(lead)
    else:
        print(f"Skipping already sent: {lead['email']}")

print(f"Verified leads ready for Batch 7: {len(verified_batch7)}")
with open("scratch/ready_leads_batch7.json", "w", encoding="utf-8") as f:
    json.dump(verified_batch7, f, ensure_ascii=False, indent=2)
