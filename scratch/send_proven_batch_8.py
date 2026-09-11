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

with open("scratch/ready_leads_batch8.json", "r", encoding="utf-8") as f:
    leads = json.load(f)

print(f"Pokrecem slanje za {len(leads)} verifikovanih kontakata iz Batch 8...\n")
sys.stdout.flush()

sent_count = 0

for idx, lead in enumerate(leads, 1):
    to_email = lead["email"]
    subject = lead["subject"]
    name = lead["name"]
    niche = lead["niche"]
    url = lead["url"]
    points = lead["hook_points"]

    if niche == "heating_mfg":
        intro = f"<p>Zdravo,</p><p>Pratim tradiciju i proizvodni program grejnih sistema kompanije {name}. Pred-zimska sezona nabavke kotlova na pelet i grejnih tela dostiže vrhunac upravo sada — kupci sa telefona traže brz uvid u karakteristike, kvadraturu i najbliže prodajno mesto.</p>"
    elif niche == "custom_kitchens":
        intro = f"<p>Zdravo,</p><p>Pratim izvedene radove i dizajn enterijera brenda {name}. Kupci koji ulažu u modernu kuhinju po meri inspiraciju traže sa telefona — mobilna prezentacija mora u sekundi prikazati kvalitet materijala i omogućiti slanje skice.</p>"
    elif niche == "legal":
        intro = f"<p>Poštovani,</p><p>Pratim ekspertizu i ugled advokatskog tima {name}. Direktori kompanija i investitori koji traže pravno zastupanje u privredi i nekretninama pretražuju sa mobilnih telefona — sajt mora odavati autoritet i omogućiti direktan kontakt.</p>"
    else: # auto_service
        intro = f"<p>Zdravo,</p><p>Pratim rad i profesionalne servisne usluge tima {name}. Vlasnici vozila u kvaru ili pred redovan servis sa telefona biraju servis koji nudi zakazivanje termina u 2 klika bez poziva i čekanja.</p>"

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
