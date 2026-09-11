import json

leads_data = [
    # 1. Proizvođači kotlova na pelet i grejnih sistema (Pik sezone grejanja)
    {
        "niche": "heating_mfg",
        "name": "Alfa-Plam Vranje",
        "email": "firma@alfaplam.rs",
        "url": "https://alfaplam.rs/",
        "subject": "Pitanje u vezi maloprodajne mreže i kotlova na alfaplam.rs",
        "hook_points": [
            "Mobilni konfigurator za odabir kotla i grejnog tela prema kvadraturi stana.",
            "Ubrzanje ucitavanja masivnog kataloga i tehnickih sema na mobilnoj mrezi.",
            "Google SEO optimizacija za pretrage kotlova na pelet pred grejnu sezonu."
        ]
    },
    {
        "niche": "heating_mfg",
        "name": "Termomont Šimanovci",
        "email": "prodajnicentar@termomont.rs",
        "url": "https://termomont.rs/",
        "subject": "Pitanje u vezi prodajnog centra i kotlova na termomont.rs",
        "hook_points": [
            "Brzi kalkulator snage kotla i zahtev za ponudu u 2 klika sa telefona.",
            "Smanjenje opterecenja tehnickih uputstava i kataloga na 4G mrezi.",
            "Google rang za kotlove na pelet, biomasu i toplotne pumpe."
        ]
    },
    {
        "niche": "heating_mfg",
        "name": "Radijator Inženjering Kraljevo",
        "email": "radijator@radijator.rs",
        "url": "https://radijator.rs/",
        "subject": "Pitanje u vezi prezentacije kotlova na radijator.rs",
        "hook_points": [
            "Pojednostavljen mobilni pristup distributivnoj i servisnoj mrezi po gradovima.",
            "Kompresija specifikacija industrijskih i kucnih kotlova za telefone.",
            "Corporate SEO rang za grejne sisteme u Srbiji i regionu."
        ]
    },
    {
        "niche": "heating_mfg",
        "name": "Kepo Kotlovi na pelet",
        "email": "tehnickapodrska@kepo.rs",
        "url": "https://kepo.rs/",
        "subject": "Pitanje u vezi tehnicke podrske i prodaje na kepo.rs",
        "hook_points": [
            "Mobilna pretraga ovlascenih servisera i montazera u 1 klik.",
            "Ubrzanje otvaranja prikaza modela i dodatne opreme na mobilnom.",
            "Google pozicioniranje za pelet kotlove i sobne peci."
        ]
    },

    # 2. Kuhinje po meri & Plakari (Visoka karta: 1.500€–5.000€)
    {
        "niche": "custom_kitchens",
        "name": "Dipo Kuhinje",
        "email": "office@dipo.rs",
        "url": "https://dipo.rs/",
        "subject": "Pitanje u vezi zakazivanja 3D projektovanja na dipo.rs",
        "hook_points": [
            "Mobilni formular za slanje skice i dimenzija kuhinje u 2 klika sa telefona.",
            "Ubrzanje galerije izvedenih kuhinja i okova na mobilnoj 4G mrezi.",
            "Google pozicioniranje za moderne kuhinje po meri u Beogradu."
        ]
    },
    {
        "niche": "custom_kitchens",
        "name": "Lignum Kuhinje i Nameštaj",
        "email": "office@lignum.rs",
        "url": "https://lignum.rs/",
        "subject": "Pitanje u vezi prezentacije i kuhinja na lignum.rs",
        "hook_points": [
            "Fiksirano dugme 'Zatrazite proracun kuhinje' pri skrolovanju na telefonu.",
            "Optimizacija fotografija premijum materijala (MDF, masiv) bez zastoja.",
            "Lokalni Google SEO za dizajn i izradu namestaja po meri."
        ]
    },

    # 3. Advokatske kancelarije za privredu & B2B ugovore (Veliki retaineri)
    {
        "niche": "legal",
        "name": "Vuković i Partneri AOD",
        "email": "info@vp.rs",
        "url": "https://vp.rs/",
        "subject": "Pitanje u vezi prezentacije privrednog prava na vp.rs",
        "hook_points": [
            "Mobilna forma za korporativne klijente i zakazivanje pravnih konsultacija.",
            "Optimizacija otvaranja pravnih analiza i vesti na mobilnom internetu.",
            "Corporate SEO dominacija za privredno, bankarsko i radno pravo."
        ]
    },
    {
        "niche": "legal",
        "name": "Živković Samardžić Advokati",
        "email": "office@zslaw.rs",
        "url": "https://zslaw.rs/",
        "subject": "Pitanje u vezi prezentacije zslaw.rs",
        "hook_points": [
            "Pojednostavljen kontakt i uvid u specijalizacije tima lekara i advokata sa telefona.",
            "Smanjenje opterecenja publikacija i vodicak na 4G mrezi.",
            "Google rang za vodece advokatske kancelarije za nekretnine i corporate law."
        ]
    },
    {
        "niche": "legal",
        "name": "Gecić Law Kancelarija",
        "email": "office@geciclaw.com",
        "url": "https://geciclaw.com/",
        "subject": "Pitanje u vezi prezentacije geciclaw.com",
        "hook_points": [
            "Ubrzanje pristupa informacijama o M&A, ESG i regulatornim praksama na telefonu.",
            "Mobilno zakazivanje sastanaka za domace i inostrane kompanije u 2 klika.",
            "International Google rang za poslovno pravo u Jugoistocnoj Evropi."
        ]
    },
    {
        "niche": "legal",
        "name": "Stanković i Partneri Advokati",
        "email": "nebojsa@nebojsa.com",
        "url": "https://stankovicandpartners.com/",
        "subject": "Pitanje u vezi prezentacije stankovicandpartners.com",
        "hook_points": [
            "Pojednostavljen kontakt za privredne sporove i investicione projekte.",
            "Kompresija profila tima advokata za rad bez zastoja na telefonu.",
            "Google pozicije za privredno pravo i zastupanje."
        ]
    },

    # 4. Premijum auto-servisi & Specijalizovana mehanika
    {
        "niche": "auto_service",
        "name": "BMW Servis Radulović",
        "email": "office@radulovic-group.com",
        "url": "https://radulovic-group.com/",
        "subject": "Pitanje u vezi online zakazivanja servisa na radulovic-group.com",
        "hook_points": [
            "Mobilni buking redovnog servisa i dijagnostike u 2 klika sa telefona.",
            "Ubrzanje prikaza servisnih paketa i ponude vozila na mobilnoj mrezi.",
            "Google rang za servisiranje BMW i MINI vozila u Beogradu i Novom Sadu."
        ]
    },
    {
        "niche": "auto_service",
        "name": "Auto Centar Petrović",
        "email": "kontakt@autocentarpetrovic.rs",
        "url": "https://autocentarpetrovic.rs/",
        "subject": "Pitanje u vezi zakazivanja mehanike na autocentarpetrovic.rs",
        "hook_points": [
            "Fiksirano dugme 'Zakazite pregled vozila' pri skrolovanju na dnu ekrana.",
            "Prikaz cenovnika i spiska intervencija prilagodjen mobilnom ekranu.",
            "Lokalni Google SEO za auto-servise i dijagnostiku."
        ]
    }
]

with open('.mp/sent_emails_history.txt', 'r', encoding='utf-8', errors='ignore') as f:
    history = set(line.strip().lower() for line in f if line.strip())

verified_batch8 = []
for lead in leads_data:
    if lead['email'].lower() not in history:
        verified_batch8.append(lead)
    else:
        print(f"Skipping already sent: {lead['email']}")

print(f"Verified leads ready for Batch 8: {len(verified_batch8)}")
with open("scratch/ready_leads_batch8.json", "w", encoding="utf-8") as f:
    json.dump(verified_batch8, f, ensure_ascii=False, indent=2)
