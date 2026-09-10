import json

leads_data = [
    # 1. Estetska i plastična hirurgija (2.000€–5.000€ po pacijentu)
    {
        "niche": "surgery",
        "name": "Ordinacija dr Stojićević",
        "email": "vladimir@stojicevic.rs",
        "url": "https://stojicevic.rs/",
        "subject": "Pitanje u vezi mobilnog zakazivanja na stojicevic.rs",
        "hook_points": [
            "Mobilno slanje fotografija i upita za konsultacije u 2 klika sa telefona.",
            "Ubrzanje otvaranja prikaza estetskih rezultata i tima lekara na 4G mrezi.",
            "Google pozicioniranje za estetsku hirurgiju i antiejdzing u Beogradu."
        ]
    },

    # 2. ALU & PVC stolarija, fasade & rolo sistemi (3.000€–30.000€ ugovori)
    {
        "niche": "fenestration",
        "name": "Sunce Marinković Kragujevac",
        "email": "office@suncemarinkovic.com",
        "url": "https://suncemarinkovic.com/",
        "subject": "Pitanje u vezi prezentacije i B2B upita na suncemarinkovic.com",
        "hook_points": [
            "Kalkulator dimenzija i brzi zahtev za ponudu u 2 klika sa telefona.",
            "Ubrzanje tehnickih kataloga i prikaza referenci na mobilnom internetu.",
            "Google rang za aluminijumsku i PVC stolariju i staklene fasade."
        ]
    },
    {
        "niche": "fenestration",
        "name": "Betaplast Novi Sad",
        "email": "info@betaplast.rs",
        "url": "https://betaplast.rs/",
        "subject": "Pitanje u vezi betaplast.rs i zakazivanja merenja",
        "hook_points": [
            "Fiksirano dugme 'Pozovite za besplatno merenje' pri skrolovanju na dnu ekrana.",
            "Kompresija slika montiranih portala i stolarije za trenutni rad na telefonu.",
            "Lokalni SEO profil za PVC i ALU stolariju u Novom Sadu i Vojvodini."
        ]
    },
    {
        "niche": "fenestration",
        "name": "Aluroll Batočina",
        "email": "design@aluroll.rs",
        "url": "https://aluroll.rs/",
        "subject": "Pitanje u vezi prezentacije rolo i fasadnih sistema na aluroll.rs",
        "hook_points": [
            "Mobilni katalog rolo vrata, segmentnih vrata i fasada prilagodjen 4G mrezi.",
            "Olakšano slanje projektnih specifikacija za investitore u 2 klika sa telefona.",
            "Google rang za industrijska rolo vrata i fasadnu bravariju."
        ]
    },
    {
        "niche": "fenestration",
        "name": "Megaplast PVC",
        "email": "officebg@megaplast.rs",
        "url": "https://megaplast.rs/",
        "subject": "Pitanje u vezi mobilne verzije sajta megaplast.rs",
        "hook_points": [
            "Direktan taster za brzi proracun cene stolarije i zakazivanje merenja.",
            "Smanjenje opterecenja galerija i profila za rad bez zastoja na telefonu.",
            "Google pozicioniranje za PVC stolariju i roletne u Beogradu."
        ]
    },
    {
        "niche": "fenestration",
        "name": "Hram 032 Stolarija",
        "email": "mpo.preljina@hram032.rs",
        "url": "https://hram032.rs/",
        "subject": "Pitanje u vezi online kataloga i maloprodaje na hram032.rs",
        "hook_points": [
            "Mobilni pregled asortimana sobnih i ulaznih vrata po salonima sa telefona.",
            "Ubrzanje ucitavanja akcija i cenovnika na mobilnoj mrezi.",
            "Google pozicioniranje za maloprodajnu mrezu stolarije u Srbiji."
        ]
    },
    {
        "niche": "fenestration",
        "name": "Roplasto PVC",
        "email": "totalprofil@gmail.com",
        "url": "https://roplasto.rs/",
        "subject": "Pitanje u vezi roplasto.rs i upita za stolariju",
        "hook_points": [
            "Postavljanje WhatsApp i mobilnog dugmeta za hitan kontakt pri dnu ekrana.",
            "Optimizacija tehnickih specifikacija nemackih profila za mobilni prikaz.",
            "Google profil za pretrage PVC profila i ugradnje prozora."
        ]
    },

    # 3. Veterinarske bolnice (hitne intervencije 24/7)
    {
        "niche": "veterinary",
        "name": "Veterinarska klinika Novak",
        "email": "novak@ptt.rs",
        "url": "https://vetnovak.com/",
        "subject": "Pitanje u vezi hitnog zakazivanja na vetnovak.com",
        "hook_points": [
            "Uocljivo 'Dezurna sluzba 24/7 - Pozovite odmah' dugme fiksirano na mobilnom.",
            "Ubrzanje ucitavanja stranica sa dijagnostikom i timom veterinara na 4G.",
            "Google rang za hitnu veterinarsku pomoc i operacije u Beogradu."
        ]
    },

    # 4. Privatne poliklinike & Medicina
    {
        "niche": "medical",
        "name": "Poliklinika Sunce Kragujevac",
        "email": "psunce@yahoo.com",
        "url": "https://poliklinikasunce.com/",
        "subject": "Pitanje u vezi zakazivanja pregleda u Poliklinici Sunce",
        "hook_points": [
            "Mobilni formular za zakazivanje pregleda kod specijaliste bez cekanja.",
            "Optimizacija prikaza lekara i cenovnika za telefone.",
            "Lokalni Google SEO za privatnu dijagnostiku u Kragujevcu."
        ]
    },

    # 5. Toplotne pumpe & Solarni sistemi
    {
        "niche": "solar_hvac",
        "name": "Helios Solar Beograd",
        "email": "info@helios-solar.com",
        "url": "https://helios-solar.com/",
        "subject": "Pitanje u vezi proracuna za solarne panele na helios-solar.com",
        "hook_points": [
            "Mobilni solarni kalkulator ustede i brzi upitnik u 2 klika.",
            "Ubrzanje kataloga solarnih panela i invertera na mobilnoj mrezi.",
            "Google rang za ugradnju solara pred jesenju grejnu sezonu."
        ]
    },
    {
        "niche": "solar_hvac",
        "name": "Termo Servis Toplota",
        "email": "info@termoservis.com",
        "url": "https://termoservis.com/",
        "subject": "Pitanje u vezi servisa i montaze grejanja na termoservis.com",
        "hook_points": [
            "Brzi taster za zakazivanje servisa toplotnih pumpi i kotlova sa mobilnog.",
            "Prikaz servisnih zona i opisa intervencija prilagodjen telefonu.",
            "Google pozicioniranje pred pocetak grejne sezone."
        ]
    },

    # 6. B2B Opremanje & Hotelijerstvo (Velike karte)
    {
        "niche": "b2b_fitout",
        "name": "Simpo Opremanje Hotela",
        "email": "office@simpo.rs",
        "url": "https://simpo.rs/",
        "subject": "Pitanje u vezi B2B opremanja i hotelskih referenci na simpo.rs",
        "hook_points": [
            "Mobilni B2B upitnik za investitore i slanje specifikacija opremanja u 2 klika.",
            "Optimizacija galerije opremljenih hotela i rezidencija za rad na 4G mrezi.",
            "Corporate SEO dominacija za opremanje hotela i poslovnih prostora."
        ]
    }
]

with open('.mp/sent_emails_history.txt', 'r', encoding='utf-8', errors='ignore') as f:
    history = set(line.strip().lower() for line in f if line.strip())

verified_batch4 = []
for lead in leads_data:
    if lead['email'].lower() not in history:
        verified_batch4.append(lead)
    else:
        print(f"Skipping already sent: {lead['email']}")

print(f"Verified leads ready for Batch 4: {len(verified_batch4)}")
with open("scratch/ready_leads_batch4.json", "w", encoding="utf-8") as f:
    json.dump(verified_batch4, f, ensure_ascii=False, indent=2)
