import json

leads_data = [
    # 1. Magnetna rezonanca, CT skener & Radiologija (150€–400€ po pregledu)
    {
        "niche": "radiology",
        "name": "Dijagnostički Centar Hram",
        "email": "office@dchram.rs",
        "url": "https://dchram.rs/",
        "subject": "Pitanje u vezi zakazivanja magnetne rezonance na dchram.rs",
        "hook_points": [
            "Mobilni formular za zakazivanje termina MR snimanja u 2 klika sa telefona.",
            "Ubrzanje ucitavanja stranica sa cenovnikom i timom radiologa na 4G mrezi.",
            "Google rang za magnetnu rezonancu i skener na Vracaru i u Beogradu."
        ]
    },
    {
        "niche": "radiology",
        "name": "Magnetna Rezonanca Centar",
        "email": "domzdravljamr@gmail.com",
        "url": "https://magnetnarezonanca.rs/",
        "subject": "Pitanje u vezi mobilnog zakazivanja na magnetnarezonanca.rs",
        "hook_points": [
            "Fiksirano dugme 'Zakazite MR snimanje bez cekanja' na dnu ekrana.",
            "Pojednostavljen mobilni vodic za pripremu pacijenta pred pregled.",
            "Google pozicioniranje za hitna radioloska snimanja."
        ]
    },

    # 2. Profesionalna ugostiteljska & Pekarska oprema (2.000€–20.000€ ugovori)
    {
        "niche": "gastro_equipment",
        "name": "Gastro Oprema Srbija",
        "email": "prodaja@gastrooprema.rs",
        "url": "https://gastrooprema.rs/",
        "subject": "Pitanje u vezi profesionalne ugostiteljske opreme na gastrooprema.rs",
        "hook_points": [
            "Mobilni B2B katalog konvektomata i pica peci prilagodjen 4G mrezi.",
            "Brzi zahtev za ponudu i specifikaciju kuhinje u 2 klika sa telefona.",
            "Google rang za profesionalnu opremu za restorane i pekare."
        ]
    },
    {
        "niche": "gastro_equipment",
        "name": "Bago Ugostiteljska Oprema",
        "email": "nis@bago.rs",
        "url": "https://bago.rs/",
        "subject": "Pitanje u vezi prezentacije i opremanja kuhinja na bago.rs",
        "hook_points": [
            "Kompresija tehnickih kataloga i sema rashladnih stolova za telefone.",
            "Olakšano slanje projektnih zahteva za ugostitelje sa mobilnog.",
            "Google pozicioniranje za opremu za ketering i hotele."
        ]
    },

    # 3. Poljoprivredna mehanizacija, traktori & navodnjavanje (5.000€–100.000€)
    {
        "niche": "agri_machinery",
        "name": "Kite DOO (John Deere Srbija)",
        "email": "goran.demkorihter@kitedoo.rs",
        "url": "https://kitedoo.rs/",
        "subject": "Pitanje u vezi prezentacije mehanizacije na kitedoo.rs",
        "hook_points": [
            "Mobilni konfigurator traktora i prikljucnih masina prilagodjen poljoprivrednicima.",
            "Ubrzanje kataloga rezervnih delova i servisnih centara na mobilnoj mrezi.",
            "Corporate Google dominacija za premijum poljoprivredne masine."
        ]
    },
    {
        "niche": "agri_machinery",
        "name": "Agropanonka Traktori",
        "email": "office@agropanonka.com",
        "url": "https://agropanonka.com/",
        "subject": "Pitanje u vezi ponude traktora na agropanonka.com",
        "hook_points": [
            "Kalkulator subvencija i zahtev za ponudu traktora u 2 klika sa telefona.",
            "Smanjenje opterecenja tehnickih karakteristika Belarus i Mahindra masina.",
            "Google rang za prodaju traktora i poljoprivredne mehanizacije."
        ]
    },
    {
        "niche": "agri_machinery",
        "name": "Agromarket Mehanizacija",
        "email": "webshop@agromarket.rs",
        "url": "https://agromarket.rs/",
        "subject": "Pitanje u vezi online porucivanja opreme na agromarket.rs",
        "hook_points": [
            "Mobilni pregled sistema za navodnjavanje i alata sa telefona bez zastoja.",
            "Optimizacija pretrage artikala i filtera na mobilnom internetu.",
            "Google rang za sisteme kap po kap i agromehanizaciju."
        ]
    },

    # 4. Dermatologija & Laserska medicina
    {
        "niche": "dermatology",
        "name": "Epilion Poliklinika",
        "email": "info@epilion.rs",
        "url": "https://epilion.rs/",
        "subject": "Pitanje u vezi zakazivanja laserskih tretmana na epilion.rs",
        "hook_points": [
            "Mobilno zakazivanje dermatoloskih pregleda i epilacije u 2 klika.",
            "Ubrzanje prikaza rezultata estetskih tretmana na 4G mrezi.",
            "Google pozicije za lasersku dermatologiju u Beogradu."
        ]
    },

    # 5. Tehnički pregled & Registracija vozila
    {
        "niche": "auto_inspection",
        "name": "Tehnički Pregled Auto Servis VMS",
        "email": "autocentarvms@gmail.com",
        "url": "https://tehnickipregled.rs/",
        "subject": "Pitanje u vezi online zakazivanja tehnickog pregleda na telefonu",
        "hook_points": [
            "Kalkulator cene registracije vozila i zakazivanje termina u 2 klika sa telefona.",
            "Fiksirano dugme 'Zakazite termin tehnickog pregleda' na dnu ekrana.",
            "Lokalni Google SEO za tehnicki pregled i osiguranje vozila."
        ]
    }
]

with open('.mp/sent_emails_history.txt', 'r', encoding='utf-8', errors='ignore') as f:
    history = set(line.strip().lower() for line in f if line.strip())

verified_batch9 = []
for lead in leads_data:
    if lead['email'].lower() not in history:
        verified_batch9.append(lead)
    else:
        print(f"Skipping already sent: {lead['email']}")

print(f"Verified leads ready for Batch 9: {len(verified_batch9)}")
with open("scratch/ready_leads_batch9.json", "w", encoding="utf-8") as f:
    json.dump(verified_batch9, f, ensure_ascii=False, indent=2)
