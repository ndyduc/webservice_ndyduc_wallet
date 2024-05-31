import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(email):
    fromaddr = 'duc20021118@gmail.com'
    verify = ''.join(random.choices('0123456789', k=6))
    mime_msg = MIMEText(verify)
    
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = email
    msg['Subject'] = '_ndyduc_ wallet verify code'
    msg.attach(mime_msg)

    username = 'duc20021118@gmail.com'
    password = 'byll xaks nrgu owlf' 

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.sendmail(fromaddr, email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
        return verify
    except Exception as e:
        print("Unable to send email:", e)
        return False
