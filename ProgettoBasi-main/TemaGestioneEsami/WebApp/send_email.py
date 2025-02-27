
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def generate_random_number():
    random_number = random.randint(0, 999999)
    formatted_number = f"{random_number:06d}"
    return formatted_number


def send_email(subject, body):
    sender_email = "pagregzem2023@libero.it" #mettete una mail libero.it
    sender_password = "Angelo99!!!"
    recipient_email = "destinatario@example.com"

    # Create a MIMEText object with UTF-8 encoding
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP("smtp.libero.it", 587) as server:
            server.starttls()  # Avvia la connessione TLS (Transport Layer Security)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print("Email inviata con successo!")
    except Exception as e:
        print(f"Errore durante l'invio dell'email: {e}")

if __name__ == "__main__":
    subject = "Matricola per iscrizione"
    Matricola = generate_random_number()
    body = "La tua Matricola per iscriverti è: "+Matricola
    send_email(subject, body)
