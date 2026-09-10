import smtplib
import time
import json
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "ivanbradic.biz@gmail.com"
SMTP_PASS = "excw jilu pgso kevf"

with open("scratch/ready_leads_batch4.json", "r", encoding="utf-8") as f:
    leads = json.load(f)

print(f"Pokrecem slanje za {len(leads)} verifikovanih kontakata iz Batch 4...\n")
sys.stdout.flush()

sent_count = 0

for idx, lead in enumerate(leads, 1):
    to_email = lead["email"]
    subject = lead["subject"]
    name = lead["name"]
    niche = lead["niche"]
    url = lead["url"]
    points = lead["hook_points"]

    if niche == "surgery":
        intro = f"<p>Poštovani,</p><p>Pratim rad i reputaciju ordinacije {name} (preko 3.000 uspešnih estetskih zahvata). Pacijenti koji biraju estetske intervencije od nekoliko hiljada evra odluku donose pažljivim istraživanjem sa mobilnog telefona — sajt u prve 3 sekunde mora uliti apsolutno poverenje.</p>"
    elif niche == "fenestration":
        intro = f"<p>Zdravo,</p><p>Pratim proizvodni program i reference kompanije {name}. Investitori i kupci koji traže zamenu stolarije, staklene fasade ili rolo sisteme na zgradama i kućama pretražuju sa telefona i traže brzu procenu troškova.</p>"
    elif niche == "veterinary":
        intro = f"<p>Poštovani,</p><p>Pratim rad i višedecenijsku reputaciju tima {name}. Kod hitnih intervencija i dežurstava, vlasnici ljubimaca u panici na telefonima traže pomoć — mobilni sajt mora omogućiti poziv u jednom dodiru bez skrolovanja.</p>"
    elif niche == "solar_hvac":
        intro = f"<p>Zdravo,</p><p>Pred-zimska sezona grejanja i ugradnje solarnih sistema počinje upravo sada. Klijenti na mobilnim telefonima pretražuju opcije i biraju izvođača gde je u 2 klika moguće dobiti proračun ili procenu.</p>"
    elif niche == "b2b_fitout":
        intro = f"<p>Zdravo,</p><p>Pratim velike B2B projekte i opremanje objekata kompanije {name}. Kod višemilionskih ugovora za opremanje hotela i rezidencija, investitori sa mobilnog telefona očekuju trenutni uvid u katalog i reference bez čekanja.</p>"
    else: # medical
        intro = f"<p>Poštovani,</p><p>Gledao sam ponudu i medicinske usluge ustanove {name}. Kod specijalističkih pregleda i dijagnostike, pacijenti sa telefona očekuju jednostavan uvid u lekare, cene i zakazivanje u par klikova.</p>"

    html_body = f"""<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; color: #222; line-height: 1.6; font-size: 15px; max-width: 600px;">
{intro}

<p>Tri stvari koje na vašem sajtu odmah unapređuju mobilni odziv i konverziju:</p>
<ol>
  <li><strong>{points[0].split(':')[0]}:</strong> {points[0]}</li>
  <li><strong>{points[1].split(':')[0]}:</strong> {points[1]}</li>
  <li><strong>{points[2].split(':')[0]}:</strong> {points[2]}</li>
</ol>

<p>Mogu da vam rešim ovu optimizaciju ove nedelje po fiksnoj ceni. Navedene 3 tačke možete proveriti i sami sa telefona za par minuta.</p>

<p>Pozdrav,<br>
<strong>Ivan Bradić</strong><br>
Web Development & Conversion Optimization<br>
<a href="https://ivanbradic.vercel.app" style="color: #2563eb;">ivanbradic.vercel.app</a></p>
</body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()

        sent_count += 1
        safe_name = name.encode('ascii', 'replace').decode('ascii')
        print(f"USPESNO [{idx}/{len(leads)}] Poslato na {to_email} ({safe_name})")
        sys.stdout.flush()

        with open(".mp/sent_emails_history.txt", "a", encoding="utf-8") as f:
            f.write(f"{to_email}\n")

        if idx < len(leads):
            print("Cekam 20s pre sledeceg slanja...")
            sys.stdout.flush()
            time.sleep(20)

    except Exception as e:
        safe_err = str(e).encode('ascii', 'replace').decode('ascii')
        print(f"GRESKA [{idx}/{len(leads)}] Pri slanju na {to_email}: {safe_err}")
        sys.stdout.flush()

print(f"\nZAVRSENO! Uspesno poslato {sent_count}/{len(leads)} mejlova.")
sys.stdout.flush()
