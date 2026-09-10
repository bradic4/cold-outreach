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

with open("scratch/ready_leads_batch5.json", "r", encoding="utf-8") as f:
    leads = json.load(f)

print(f"Pokrecem slanje za {len(leads)} verifikovanih kontakata iz Batch 5...\n")
sys.stdout.flush()

sent_count = 0

for idx, lead in enumerate(leads, 1):
    to_email = lead["email"]
    subject = lead["subject"]
    name = lead["name"]
    niche = lead["niche"]
    url = lead["url"]
    points = lead["hook_points"]

    if niche == "events":
        intro = f"<p>Zdravo,</p><p>Pratim rad i prestižnu reputaciju prostora {name}. Mladenci i korporativni klijenti koji organizuju proslave od nekoliko hiljada evra prvu selekciju prostora prave gledajući fotografije sa telefona — sajt mora u sekundi preneti atmosferu i olakšati slanje upita.</p>"
    elif niche == "flooring_insulation":
        intro = f"<p>Zdravo,</p><p>Pratim izvedene radove i reference kompanije {name}. Investitori i vlasnici objekata koji traže industrijske podove ili hidroizolaciju pretražuju sa telefona i traže brzu procenu kvadrature i cene.</p>"
    elif niche == "accounting":
        intro = f"<p>Poštovani,</p><p>Pratim ponudu i stručnost računovodstvenog tima {name}. Preduzetnici i direktori firmi koji traže pouzdano knjigovodstvo pretražuju sa telefona i biraju tim koji pruža jasan uvid u pakete usluga i brz kontakt.</p>"
    elif niche == "driving_school":
        intro = f"<p>Zdravo,</p><p>Pratim rad i uspešnost obuke u timu {name}. Mladi kandidati i budući vozači danas sve rade sa mobilnog telefona — auto-škola koja ponudi lak online upis u 2 klika dobija većinu novih polaznika.</p>"
    else: # medical
        intro = f"<p>Poštovani,</p><p>Pratim rad i dijagnostičke usluge {name}. Pacijenti sa mobilnih telefona očekuju jednostavan uvid u analize, pripremu i lokacije laboratorija bez lutanja po sajtu.</p>"

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
