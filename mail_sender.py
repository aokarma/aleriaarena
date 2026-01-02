import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "serwer2515494.home.pl"
SMTP_PORT = 587
SMTP_USER = "bok@galeriaarena.pl"
SMTP_PASS = "Mzpdp2024!"

msg = MIMEText("Testowa wiadomość z Python + home.pl (TLS)")
msg["Subject"] = "Test SMTP TLS"
msg["From"] = SMTP_USER
msg["To"] = SMTP_USER

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [SMTP_USER], msg.as_string())
        print("Wiadomość wysłana poprawnie!")
except Exception as e:
    print("Błąd:", e)
