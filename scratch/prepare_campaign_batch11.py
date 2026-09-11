import json

leads_data = [
    # 1. Privatni domovi za stara lica & Nega (800€–1.500€/mesečno - visoka konverzija)
    {
        "niche": "nursing_homes",
        "name": "Dom za stara lica Senior Plus",
        "email": "starackidomseniorplus@gmail.com",
        "url": "https://seniorplus.rs/",
        "subject": "Pitanje u vezi prezentacije i smestaja na seniorplus.rs",
        "hook_points": [
            "Mobilni formular za upit slobodnih mesta i zakazivanje posete domu u 2 klika.",
            "Ubrzanje ucitavanja fotografija soba, dvorista i medicinske nege na 4G mrezi.",
            "Google rang za privatne domove za stare i negu nepokretnih lica u Beogradu."
        ]
    },
    {
        "niche": "nursing_homes",
        "name": "Dom za stara lica Nana",
        "email": "domnana09@gmail.com",
        "url": "https://domnana.rs/",
        "subject": "Pitanje u vezi mobilnog zakazivanja posete na domnana.rs",
        "hook_points": [
            "Fiksirano dugme 'Pozovite za prijem i informacije' na dnu mobilnog ekrana.",
            "Optimizacija prikaza paketa smestaja i medicinskih usluga za telefone.",
            "Lokalni Google SEO profil za licencirane domove za stare."
        ]
    },

    # 2. Mermer, granit & Kvarcne radne ploče (1.000€–10.000€)
    {
        "niche": "stone_granite",
        "name": "Mermer Granit Breza",
        "email": "desk@breza.rs",
        "url": "https://breza.rs/",
        "subject": "Pitanje u vezi mermernih i granitnih ploca na breza.rs",
        "hook_points": [
            "Mobilni kalkulator kvadrature i slanje mera kuhinjskih ploca u 2 klika sa telefona.",
            "Kompresija tekstura prirodnog kamena za rad bez zastoja na mobilnom internetu.",
            "Google rang za mermer, granit i kvarcne radne ploce u Srbiji."
        ]
    },

    # 3. Distributeri medicinske & Stomatološke opreme (5.000€–50.000€)
    {
        "niche": "med_tech",
        "name": "Dental Medical Srbija",
        "email": "info@dental-medical.rs",
        "url": "https://dental-medical.rs/",
        "subject": "Pitanje u vezi B2B porucivanja stomatoloske opreme na dental-medical.rs",
        "hook_points": [
            "Mobilna pretraga asortimana implantata i materijala prilagodjena stomatolozima.",
            "Ubrzanje kataloga aparata i akcija na mobilnoj 4G mrezi.",
            "Corporate SEO dominacija za stomatolosku opremu i materijale."
        ]
    },
    {
        "niche": "med_tech",
        "name": "Vicor Medicinska Oprema",
        "email": "office@vicor.rs",
        "url": "https://vicor.rs/",
        "subject": "Pitanje u vezi prezentacije medicinskih aparata na vicor.rs",
        "hook_points": [
            "Brzi B2B upitnik za ponudu ultrazvucnih i EKG aparata sa telefona u 2 klika.",
            "Smanjenje opterecenja tehnickih brosura i specifikacija na mobilnom.",
            "Google rang za medicinsku dijagnosticku opremu i servis."
        ]
    },
    {
        "niche": "med_tech",
        "name": "Medicom Šabac",
        "email": "office@medicom.rs",
        "url": "https://medicom.rs/",
        "subject": "Pitanje u vezi B2B kataloga opreme na medicom.rs",
        "hook_points": [
            "Pojednostavljen mobilni pristup sterilizaciji i aparatima za lekare.",
            "Kompresija specifikacija medicinskih uredjaja za telefone.",
            "Google pozicioniranje za medicinsku opremu i potrosni materijal."
        ]
    },
    {
        "niche": "med_tech",
        "name": "Mikodental Tehnologija",
        "email": "info@mikodental.com",
        "url": "https://mikodental.rs/",
        "subject": "Pitanje u vezi CAD/CAM tehnologije na mikodental.rs",
        "hook_points": [
            "Mobilni pregled CAD/CAM glodalica i pecica za keramiku bez cekanja na 4G.",
            "Olakšano slanje zahteva za servis i demonstraciju opreme sa telefona.",
            "Google rang za zubotehnicku opremu i digitalnu stomatologiju."
        ]
    },
    {
        "niche": "med_tech",
        "name": "Medisal Oprema",
        "email": "office@medisal.co.rs",
        "url": "https://medisal.rs/",
        "subject": "Pitanje u vezi prezentacije aparata na medisal.rs",
        "hook_points": [
            "Brzo otvaranje kataloga hirurske i dijagnosticke opreme na telefonu.",
            "Mobilni upitnik za specifikaciju i ponudu u 2 klika.",
            "Google pozicioniranje za opremanje klinika i bolnica."
        ]
    },

    # 4. Industrijska automatizacija & Merenja (B2B inženjering)
    {
        "niche": "industrial_automation",
        "name": "Automatika Beograd",
        "email": "office@automatika.rs",
        "url": "https://automatika.rs/",
        "subject": "Pitanje u vezi industrijske automatike na automatika.rs",
        "hook_points": [
            "Mobilni formular za tehnicke zahteve i automatizaciju industrijskih pogona.",
            "Ubrzanje kataloga senzora, PLC modula i regulacije na 4G mrezi.",
            "Corporate SEO rang za industrijsku elektroniku i automatiku."
        ]
    },
    {
        "niche": "industrial_automation",
        "name": "Ibis Instrumenti",
        "email": "info@ibis-instruments.com",
        "url": "https://ibis-instruments.com/",
        "subject": "Pitanje u vezi prezentacije test opreme na ibis-instruments.com",
        "hook_points": [
            "Optimizacija pristupa mernoj i telekomunikacionoj opremi za inzenjere na terenu.",
            "Smanjenje vremena otvaranja stranica resenja i softvera na mobilnom.",
            "Google rang za merne instrumente i sistemsku integraciju."
        ]
    },
    {
        "niche": "industrial_automation",
        "name": "Mikro Kontrol",
        "email": "nabavka@mikrokontrol.rs",
        "url": "https://mikrokontrol.rs/",
        "subject": "Pitanje u vezi SCADA i PLC inzenjeringa na mikrokontrol.rs",
        "hook_points": [
            "Brzi uvid u izvedene industrijske reference i ormane automatike sa telefona.",
            "Mobilno slanje projektnih specifikacija za industrijske investitore.",
            "Google pozicije za industrijsku automatizaciju i SCADA sisteme."
        ]
    },

    # 5. Psihoterapija & Privatna savetovališta
    {
        "niche": "counseling",
        "name": "Savetovalište Entera",
        "email": "office@entera.rs",
        "url": "https://entera.rs/",
        "subject": "Pitanje u vezi diskretnog online zakazivanja na entera.rs",
        "hook_points": [
            "Mobilni kalendar za diskretan odabir termina i seanse u 2 klika sa telefona.",
            "Optimizacija prikaza tema i modaliteta psihoterapije na 4G mrezi.",
            "Google pozicioniranje za individualnu i partnersku psihoterapiju."
        ]
    }
]

with open('.mp/sent_emails_history.txt', 'r', encoding='utf-8', errors='ignore') as f:
    history = set(line.strip().lower() for line in f if line.strip())

verified_batch11 = []
for lead in leads_data:
    if lead['email'].lower() not in history:
        verified_batch11.append(lead)
    else:
        print(f"Skipping already sent: {lead['email']}")

print(f"Verified leads ready for Batch 11: {len(verified_batch11)}")
with open("scratch/ready_leads_batch11.json", "w", encoding="utf-8") as f:
    json.dump(verified_batch11, f, ensure_ascii=False, indent=2)
