
import smtplib
from email.mime.text import MIMEText

# Create the message
msg = MIMEText("{IMG_1988.jpeg}")
msg["Subject"] = "Test"
msg["From"] = "trentdu4@gmail.com"
msg["To"] = "tdu011@email.latech.edu"

# Connect to the server
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
    server.login("trentdu4@gmail.com", "ifmpwrwigvmnfuuw")
    server.sendmail("trentdu4@gmail.com", "tdu011@email.latech.edu", msg.as_string())

