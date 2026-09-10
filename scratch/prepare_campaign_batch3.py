import json

leads_data = [
    # 1. Oftalmologija & Očne klinike (Visoka karta: 1.000€–3.000€ po oku)
    {
        "niche": "eye_clinic",
        "name": "Klinika LaserFocus",
        "email": "info@laserfocus.me",
        "url": "https://laserfocus.eu/",
        "subject": "Pitanje u vezi zakazivanja pregleda na laserfocus.eu",
        "hook_points": [
            "Mobilni upitnik za lasersko skidanje dioptrije u 2 klika sa telefona.",
            "Ubrzanje ucitavanja stranica sa opisima operacija i tima lekara na 4G.",
            "Google pozicioniranje za lasersku hirurgiju oka i operacije katarakte."
        ]
    },
    {
        "niche": "eye_clinic",
        "name": "Ocna Klinika Vidar",
        "email": "info@vidar.rs",
        "url": "https://vidar.rs/",
        "subject": "Pitanje u vezi mobilnog zakazivanja na vidar.rs",
        "hook_points": [
            "Fiksirano dugme 'Zakazite oftalmoloski pregled' pri skrolovanju na dnu ekrana.",
            "Optimizacija prikaza operativnih zahvata i cenovnika na telefonu.",
            "Lokalni Google SEO za očne klinike i preglede vida."
        ]
    },
    {
        "niche": "eye_clinic",
        "name": "Klinika Maja Nis",
        "email": "info@poliklinikamaja.rs",
        "url": "https://klinikamaja.rs/",
        "subject": "Pitanje u vezi prezentacije i zakazivanja za Kliniku Maja",
        "hook_points": [
            "Direktan taster za zakazivanje dijagnostike i operacija sa mobilnog.",
            "Smanjenje vremena otvaranja galerija i opisa klinike na 4G mrezi.",
            "Google rang za vodecu oftalmologiju na jugu Srbije."
        ]
    },

    # 2. Arhitektura & Projektovanje (PageSpeed ugao)
    {
        "niche": "architecture",
        "name": "Arhitektonski studio Modular",
        "email": "office@modular.rs",
        "url": "https://modular.rs/",
        "subject": "Pitanje u vezi modular.rs i ucitavanja render portfolija",
        "hook_points": [
            "Kompresija 3D rendera i projekata za otvaranje ispod 1,6s na mobilnom.",
            "Mobilni formular za investitore i slanje projektnih zadataka u 2 klika.",
            "Google rang za arhitektonsko projektovanje i modularne objekte."
        ]
    },
    {
        "niche": "architecture",
        "name": "Studio OBE Arhitekti",
        "email": "office@obe.rs",
        "url": "https://obe.rs/",
        "subject": "Pitanje u vezi prezentacije i render slika na obe.rs",
        "hook_points": [
            "Ubrzanje ucitavanja nagradjivanih enterijerskih i arhitektonskih vizuala.",
            "Mobilno dugme za brzi upit klijenata visoke platizne moci na dnu ekrana.",
            "Google profil i optimizacija za savremeni dizajn enterijera."
        ]
    },
    {
        "niche": "architecture",
        "name": "INKa Studio Arhitekti",
        "email": "info@inka.rs",
        "url": "https://inka.rs/",
        "subject": "Pitanje u vezi prezentacije inka.rs",
        "hook_points": [
            "Optimizacija portfolio slika na WebP format za trenutni rad na telefonu.",
            "Pojednostavljen kontakt i slanje tlocrta sa telefona u 2 klika.",
            "Google rang za arhitekturu, urbanizam i projektovanje."
        ]
    },
    {
        "niche": "architecture",
        "name": "Biro Arhiform",
        "email": "info@arhiform.com",
        "url": "https://arhiform.com/",
        "subject": "Pitanje u vezi prezentacije projekata na arhiform.com",
        "hook_points": [
            "Smanjenje opterecenja slika objekata za otvaranje bez cekanja na 4G.",
            "Mobilni CTA taster za projektne konsultacije i ugovaranje radova.",
            "Google pozicioniranje za arhitektonske biroe u Beogradu."
        ]
    },
    {
        "niche": "architecture",
        "name": "Studio Domino Enterijeri",
        "email": "hello@dominostudio.com",
        "url": "https://dominostudio.rs/",
        "subject": "Pitanje u vezi dominostudio.com i prezentacije enterijera",
        "hook_points": [
            "Optimizacija luksuznih fotografija enterijera za trenutni prikaz na 4G.",
            "Brzi mobilni upitnik za kvadraturu i izradu dizajnerskog projekta.",
            "Google rang za dizajn i opremanje stambenih i poslovnih prostora."
        ]
    },

    # 3. Solarni sistemi, toplotne pumpe & grejanje
    {
        "niche": "solar_hvac",
        "name": "Telefon Inzenjering",
        "email": "office@telefon-inzenjering.co.rs",
        "url": "https://telefon-inzenjering.co.rs/",
        "subject": "Pitanje u vezi ponude solarnih sistema na telefon-inzenjering.co.rs",
        "hook_points": [
            "Mobilni formular za procenu snage i solarni kalkulator u 2 klika.",
            "Ubrzanje tehnicke dokumentacije i kataloga za rad na telefonu.",
            "Google rang za ugradnju industrijskih i stambenih solarnih elektrana."
        ]
    },
    {
        "niche": "solar_hvac",
        "name": "Toplotne Pumpe Eko",
        "email": "info@loren-line.com",
        "url": "https://toplotne-pumpe.rs/",
        "subject": "Pitanje u vezi pred-zimske ugradnje toplotnih pumpi",
        "hook_points": [
            "Kalkulator ustede grejanja i brzi zahtev za proracun sa telefona.",
            "Kompresija specifikacija toplotnih pumpi za brzo otvaranje na 4G.",
            "Google pozicioniranje pred pocetak grejne sezone."
        ]
    },

    # 4. Bazeni, Saune & Luksuzno opremanje (Karte 5.000€–20.000€)
    {
        "niche": "luxury_wellness",
        "name": "Marconio Wellness",
        "email": "info@marconio.com",
        "url": "https://marconio.com/",
        "subject": "Pitanje u vezi prezentacije spa i wellness opreme na marconio.com",
        "hook_points": [
            "Mobilni katalog hidromasaznih kada, sauna i spa centara prilagodjen telefonu.",
            "Ubrzanje otvaranja premijum vizuala i specifikacija na mobilnoj mrezi.",
            "Google rang za privatne i hotelske spa i wellness projekte."
        ]
    },
    {
        "niche": "luxury_wellness",
        "name": "Bibis Bazeni i Saune",
        "email": "info@bibis.rs",
        "url": "https://bibis.rs/",
        "subject": "Pitanje u vezi prezentacije bazena i sauna na bibis.rs",
        "hook_points": [
            "Mobilni konfigurator za izbor tipa bazena i opreme u 2 klika.",
            "Optimizacija galerije izvedenih radova za rad bez zastoja na 4G.",
            "Google pozicioniranje za izgradnju bazena i sauna u Srbiji."
        ]
    },

    # 5. Stomatologija & Dental
    {
        "niche": "dental",
        "name": "Dental Centar Kragujevac",
        "email": "info@dentalcentar.rs",
        "url": "https://dentalcentar.rs/",
        "subject": "Pitanje u vezi mobilnog zakazivanja na dentalcentar.rs",
        "hook_points": [
            "Mobilno slanje ortopan snimaka u 2 klika za brzi plan implantologije.",
            "Fiksirano dugme 'Zakazite pregled' pri skrolovanju na dnu ekrana.",
            "Google pozicioniranje za stomatologiju i implantate u Kragujevcu."
        ]
    },

    # 6. Kuhinje & Enterijeri po meri
    {
        "niche": "luxury_wellness",
        "name": "Eurosalon",
        "email": "regina@eurosalon.com",
        "url": "https://eurosalon.com/",
        "subject": "Pitanje u vezi online kataloga i prezentacije na eurosalon.com",
        "hook_points": [
            "Pojednostavljen mobilni pregled kolekcija i zakazivanje projektovanja.",
            "Ubrzanje ucitavanja fotografija namestaja na mobilnom internetu.",
            "Google rang za premijum kuhinje i opremanje enterijera."
        ]
    }
]

with open('.mp/sent_emails_history.txt', 'r', encoding='utf-8', errors='ignore') as f:
    history = set(line.strip().lower() for line in f if line.strip())

verified_batch3 = []
for lead in leads_data:
    if lead['email'].lower() not in history:
        verified_batch3.append(lead)
    else:
        print(f"Skipping already sent: {lead['email']}")

print(f"Verified leads ready for Batch 3: {len(verified_batch3)}")
with open("scratch/ready_leads_batch3.json", "w", encoding="utf-8") as f:
    json.dump(verified_batch3, f, ensure_ascii=False, indent=2)
