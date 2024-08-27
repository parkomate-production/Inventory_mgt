##https://www.youtube.com/watch?v=g_j6ILT-X0k
##myaccount.google.com\

import smtplib
from email.message import EmailMessage
import os
import imghdr

sender_mail_id = 'iotproject2005@gmail.com'
password = 'amzcpdgdgbhdgfsh'

def send(subject,message, send_to):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_mail_id
    msg['To'] = send_to

    msg1 = message
    
    msg.set_content(msg1)

    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
        smtp.login(sender_mail_id,password)
        smtp.send_message(msg)

