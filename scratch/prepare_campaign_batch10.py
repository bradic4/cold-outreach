import json

leads_data = [
    # 1. Montažne kuće & Stambeni kontejneri (20.000€–80.000€ ugovori)
    {
        "niche": "modular_homes",
        "name": "Montažne Kuće Luks",
        "email": "info@montazne-kuce.rs",
        "url": "https://montazne-kuce.rs/",
        "subject": "Pitanje u vezi kataloga modela i cena na montazne-kuce.rs",
        "hook_points": [
            "Mobilni konfigurator tipskih kuca sa proracunom cene u 2 klika sa telefona.",
            "Ubrzanje ucitavanja tlocrta i 3D vizuelizacija objekata na 4G mrezi.",
            "Google rang za izgradnju montaznih kuca kljuc u ruke u Srbiji."
        ]
    },
    {
        "niche": "modular_homes",
        "name": "Eko Kuća Montažne Kuće",
        "email": "info@ekokuca.rs",
        "url": "https://ekokuca.rs/",
        "subject": "Pitanje u vezi proracuna kvadrature na ekokuca.rs",
        "hook_points": [
            "Fiksirano dugme 'Zatrazite katalog i cene kuca' na dnu mobilnog ekrana.",
            "Optimizacija fotografija montiranih kuca za rad bez zastoja na telefonu.",
            "Google pozicioniranje za ekoloske i energetske montazne objekte."
        ]
    },
    {
        "niche": "modular_homes",
        "name": "Montažne Kuće Maker Ivanjica",
        "email": "office@maker.rs",
        "url": "https://maker.rs/",
        "subject": "Pitanje u vezi prezentacije i modela na maker.rs",
        "hook_points": [
            "Olakšano slanje zahteva za ponudu i tlocrt sa mobilnih telefona.",
            "Kompresija tehnickih preseka zidova i specifikacija materijala na 4G.",
            "Lokalni i regionalni Google SEO za montazne kuce iz Ivanjice."
        ]
    },
    {
        "niche": "modular_homes",
        "name": "Argus Inženjering Kontejneri",
        "email": "finansije@argus-eng.co.rs",
        "url": "https://argus-eng.co.rs/",
        "subject": "Pitanje u vezi B2B upita za kontejnere na argus-eng.co.rs",
        "hook_points": [
            "Mobilni formular za brzi izbor dimenzija stambenih i gradjevinskih kontejnera.",
            "Ubrzanje kataloga sanitarnih i kancelarijskih modula na telefonu.",
            "Google rang za prodaju i najam kontejnera u Srbiji."
        ]
    },
    {
        "niche": "modular_homes",
        "name": "Kontejneri Beograd (Enigma Bolt)",
        "email": "office@enigmabolt.com",
        "url": "https://kontejneri.rs/",
        "subject": "Pitanje u vezi ponude stambenih modula na kontejneri.rs",
        "hook_points": [
            "Brzi kalkulator cene sa montazom i isporukom u 2 klika sa telefona.",
            "Smanjenje opterecenja galerije gotovih objekata na mobilnom internetu.",
            "Google pozicije za stambene i portirske kontejnere."
        ]
    },

    # 2. Ginekologija, 4D ultrazvuk & Prenatalna dijagnostika
    {
        "niche": "gynecology",
        "name": "Ginekološka ordinacija Demetra",
        "email": "info@demetra.rs",
        "url": "https://demetra.rs/",
        "subject": "Pitanje u vezi zakazivanja 4D ultrazvuka na demetra.rs",
        "hook_points": [
            "Mobilno zakazivanje pregleda i prenatalnih testova u 2 klika bez poziva.",
            "Ubrzanje stranica sa opisima procedura i cenovnikom na 4G mrezi.",
            "Google rang za privatne ginekoloske preglede i vodjenje trudnoce."
        ]
    },
    {
        "niche": "gynecology",
        "name": "Ginekološka ordinacija Dr Biljana Živaljević",
        "email": "biljanazivaljevic@gmail.com",
        "url": "https://drzivaljevic.com/",
        "subject": "Pitanje u vezi mobilne verzije sajta drzivaljevic.com",
        "hook_points": [
            "Fiksirano dugme 'Zakazite pregled' pri skrolovanju na telefonu.",
            "Optimizacija prikaza tima lekara i dijagnostickih aparata na telefonu.",
            "Lokalni Google profil za ginekologiju u Beogradu."
        ]
    },
    {
        "niche": "gynecology",
        "name": "Ginekološka ordinacija Mladenović",
        "email": "info@ordinacijamladenovic.rs",
        "url": "https://ordinacijamladenovic.rs/",
        "subject": "Pitanje u vezi zakazivanja pregleda na ordinacijamladenovic.rs",
        "hook_points": [
            "Pojednostavljen mobilni upitnik za izbor termina i usluge sa telefona.",
            "Kompresija medicinskih opisa za rad bez zastoja na mobilnom.",
            "Google pozicioniranje za ginekologiju i akuserstvo."
        ]
    },

    # 3. Vikend turizam & Prestižni dvorci (Svadbe i prijemi)
    {
        "niche": "tourism_venue",
        "name": "Kaštel Ečka Zrenjanin",
        "email": "office@kastelecka.com",
        "url": "https://kastelecka.com/",
        "subject": "Pitanje u vezi rezervacije termina i vencanja na kastelecka.com",
        "hook_points": [
            "Mobilni formular za upit slobodnih datuma za bajkovita vencanja i dogadjaje u 2 klika.",
            "Ubrzanje ucitavanja fotografija dvorca i restoranskih sala na 4G mrezi.",
            "Google rang za vencanja u dvorcu i vikend odmor u Vojvodini."
        ]
    },

    # 4. Geomehanika & Temeljenje
    {
        "niche": "engineering",
        "name": "Geomehanika Inženjering",
        "email": "office@geomehanika.rs",
        "url": "https://geomehanika.rs/",
        "subject": "Pitanje u vezi geomehanickih elaborata na geomehanika.rs",
        "hook_points": [
            "Mobilni formular za investitore: slanje lokacije i zahteva za geomehaniku u 2 klika.",
            "Smanjenje opterecenja referenci i opreme za busenje na mobilnom internetu.",
            "Corporate SEO rang za geotehnicka istrazivanja i fundiranje."
        ]
    }
]

with open('.mp/sent_emails_history.txt', 'r', encoding='utf-8', errors='ignore') as f:
    history = set(line.strip().lower() for line in f if line.strip())

verified_batch10 = []
for lead in leads_data:
    if lead['email'].lower() not in history:
        verified_batch10.append(lead)
    else:
        print(f"Skipping already sent: {lead['email']}")

print(f"Verified leads ready for Batch 10: {len(verified_batch10)}")
with open("scratch/ready_leads_batch10.json", "w", encoding="utf-8") as f:
    json.dump(verified_batch10, f, ensure_ascii=False, indent=2)
