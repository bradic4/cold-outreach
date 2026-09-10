import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "ivanbradic.biz@gmail.com"
SMTP_PASS = "excw jilu pgso kevf"

lead = {
    "name": "Stomatoloska ordinacija Vident",
    "email": "office@vident.rs",
    "subject": "Pitanje u vezi prezentacije na vident.rs",
    "html": """<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; color: #222; line-height: 1.6; font-size: 15px; max-width: 600px;">
<p>Zdravo,</p>

<p>Pratim rad i stomatološku praksu Stomatološka ordinacija Vident. Pacijenti iz inostranstva i domaći posetioci koji traže zubarske ili implantološke usluge prvu procenu donose preko telefona — sajt je prva ordinacija koju vide.</p>

<p>Tri stvari koje na vašem sajtu odmah unapređuju mobilni odziv i konverziju:</p>
<ol>
  <li><strong>Mobilno slanje snimaka zuba:</strong> omogućiti pacijentima slanje ortopana u 2 klika sa telefona za brzi plan terapije.</li>
  <li><strong>Ubrzanje učitavanja stranica:</strong> smanjiti vreme otvaranja opisa ordinacije i lekara na mobilnoj 4G mreži.</li>
  <li><strong>Google rang za stomatologiju:</strong> osigurati prve pozicije za premijum stomatološke usluge.</li>
</ol>

<p>Mogu da vam rešim ovu optimizaciju ove nedelje po fiksnoj ceni. Navedene 3 tačke možete proveriti i sami sa telefona za par minuta.</p>

<p>Pozdrav,<br>
<strong>Ivan Bradić</strong><br>
Web Development & Conversion Optimization<br>
<a href="https://ivanbradic.vercel.app" style="color: #2563eb;">ivanbradic.vercel.app</a></p>
</body>
</html>"""
}

to_email = lead["email"]
subject = lead["subject"]
html_body = lead["html"]

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
    print(f"USPESNO POSLATO na {to_email}!")
    with open(".mp/sent_emails_history.txt", "a", encoding="utf-8") as f:
        f.write(f"{to_email}\n")
except Exception as e:
    print(f"GRESKA: {e}")
