import json

leads_data = [
    # 1. Geodetske agencije & Katastar / Legalizacija
    {
        "niche": "geodesy",
        "name": "Geometar Beograd (GeoViv)",
        "email": "geovivbeograd@gmail.com",
        "url": "https://geometarbeograd.rs/",
        "subject": "Pitanje u vezi geodetskih usluga na geometarbeograd.rs",
        "hook_points": [
            "Mobilni formular za brzu procenu cene omedjavanja i legalizacije u 2 klika.",
            "Ubrzanje ucitavanja spiska geodetskih usluga i referenci na 4G mrezi.",
            "Lokalni Google SEO za geodetske biroe u Beogradu."
        ]
    },
    {
        "niche": "geodesy",
        "name": "Geo Centar Kragujevac",
        "email": "geocentar@gmail.com",
        "url": "https://geocentar.rs/",
        "subject": "Pitanje u vezi geodetskog biroa geocentar.rs",
        "hook_points": [
            "Fiksirano dugme 'Zatrazite geodetski snimak' pri skrolovanju na telefonu.",
            "Optimizacija prikaza usluga katastra i premera za pametne telefone.",
            "Google profil za geodetske usluge u Kragujevcu i Sumadiji."
        ]
    },

    # 2. Privatne predškolske ustanove & Vrtići (subvencije grada: 300€–500€/mesečno po detetu)
    {
        "niche": "kindergarten",
        "name": "Vrtić Povratak Prirodi",
        "email": "info@povratakprirodi.rs",
        "url": "https://povratakprirodi.rs/",
        "subject": "Pitanje u vezi upisa i subvencija na povratakprirodi.rs",
        "hook_points": [
            "Mobilni upitnik za prijavu deteta i zakazivanje obilaska vrtica u 2 klika.",
            "Kompresija slika prostora i dvorista za otvaranje bez cekanja na telefonu.",
            "Google rang za privatne vrtice sa subvencijama grada Beograda."
        ]
    },
    {
        "niche": "kindergarten",
        "name": "Predškolska ustanova Play",
        "email": "info@vrticplay.rs",
        "url": "https://vrticplay.rs/",
        "subject": "Pitanje u vezi prezentacije i upisa za Vrtić Play",
        "hook_points": [
            "Direktan taster za zakazivanje razgovora sa pedagogom sa mobilnog.",
            "Smanjenje opterecenja galerije i programa rada na 4G mrezi.",
            "Lokalni Google SEO profil za privatne predskolske ustanove."
        ]
    },
    {
        "niche": "kindergarten",
        "name": "Predškolska ustanova Mala Zvezda",
        "email": "office@malazvezda.rs",
        "url": "https://malazvezda.rs/",
        "subject": "Pitanje u vezi online upisa na malazvezda.rs",
        "hook_points": [
            "Fiksirano dugme 'Upisite dete uz gradske subvencije' na dnu ekrana.",
            "Pojednostavljen mobilni prikaz lokacija i vaspitnih grupa.",
            "Google profil za vrtice u Beogradu."
        ]
    },

    # 3. Zaštita na radu & BZR / PPZ (zakonska obaveza za firme)
    {
        "niche": "safety",
        "name": "Tehpro Zaštita na radu",
        "email": "office@tehpro.rs",
        "url": "https://tehpro.rs/",
        "subject": "Pitanje u vezi B2B upita za bezbednost na radu na tehpro.rs",
        "hook_points": [
            "Mobilni konfigurator paketa BZR i PPZ usluga za preduzeca u 2 klika.",
            "Ubrzanje otvaranja strucnih kurseva i kataloga obuka na mobilnom.",
            "Google rang za bezbednost i zdravlje na radu u Srbiji."
        ]
    },

    # 4. Industrijska rashlada, čileri & vitrine (Veliki B2B sistemi)
    {
        "niche": "refrigeration",
        "name": "Frigo Žika",
        "email": "info@frigozika.rs",
        "url": "https://frigozika.rs/",
        "subject": "Pitanje u vezi rashladnih vitrina i opreme na frigozika.rs",
        "hook_points": [
            "Mobilni B2B katalog rashladne opreme za markete i ugostiteljstvo na 4G.",
            "Brzo slanje specifikacija i zahteva za ponudu sa telefona u 2 klika.",
            "Google pozicioniranje za industrijsku rashladu i profesionalne vitrine."
        ]
    },
    {
        "niche": "refrigeration",
        "name": "Master Frigo",
        "email": "prodaja@masterfrigo.com",
        "url": "https://masterfrigo.com/",
        "subject": "Pitanje u vezi industrijskih hladnjaca na masterfrigo.com",
        "hook_points": [
            "Optimizacija ucitavanja tehnickih sema i referenci hladnjaca na telefonu.",
            "Mobilni upitnik za proracun rashladnih komora i panela u 2 klika.",
            "Corporate SEO rang za rashladna postrojenja i industriju."
        ]
    },
    {
        "niche": "refrigeration",
        "name": "Frigomont Niš",
        "email": "frigomontnis@yahoo.com",
        "url": "https://frigomont.rs/",
        "subject": "Pitanje u vezi servisa i montaze rashlade na frigomont.rs",
        "hook_points": [
            "Taster za hitne servisne intervencije na rashladnim sistemima fiksiran na mobilnom.",
            "Prikaz asortimana klima komora i rezervnih delova na 4G mrezi.",
            "Google pozicioniranje za rashladne sisteme na jugu Srbije."
        ]
    },

    # 5. Špedicija, Carinjenje & Transport
    {
        "niche": "logistics",
        "name": "Milšped Tim",
        "email": "milsped.tim@milsped.com",
        "url": "https://milsped.com/",
        "subject": "Pitanje u vezi upita za transport i carinjenje na milsped.com",
        "hook_points": [
            "Mobilni kalkulator za brzi upit cene transporta i carinskog posredovanja.",
            "Ubrzanje pristupa informacijama o pracenju posiljaka za B2B klijente.",
            "Corporate Google dominacija za regionalnu logistiku i spediciju."
        ]
    },
    {
        "niche": "logistics",
        "name": "Gebruder Weiss Srbija",
        "email": "service@gw-world.com",
        "url": "https://gw-world.com/",
        "subject": "Pitanje u vezi korisnickog odziva za gw-world.com",
        "hook_points": [
            "Pojednostavljen mobilni kontakt za drumski i avio transport u 2 klika.",
            "Kompresija dokumenata i formi za rad bez zastoja na mobilnoj mrezi.",
            "Google rang za logisticke i skladisne usluge u Srbiji."
        ]
    }
]

with open('.mp/sent_emails_history.txt', 'r', encoding='utf-8', errors='ignore') as f:
    history = set(line.strip().lower() for line in f if line.strip())

verified_batch6 = []
for lead in leads_data:
    if lead['email'].lower() not in history:
        verified_batch6.append(lead)
    else:
        print(f"Skipping already sent: {lead['email']}")

print(f"Verified leads ready for Batch 6: {len(verified_batch6)}")
with open("scratch/ready_leads_batch6.json", "w", encoding="utf-8") as f:
    json.dump(verified_batch6, f, ensure_ascii=False, indent=2)
