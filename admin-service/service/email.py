import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logging.basicConfig(level=logging.INFO)

#
# 이메일 전송 함수
def send_approval_email(receiver_email, subject, body):
    sender_email = "teereal@naver.com"
    sender_password = "WEDVPB9ZUMJF"



    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.naver.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email,receiver_email , msg.as_string())
        server.quit()
        logging.info("Email sent successfully to %s", receiver_email)
    except Exception as e:
        logging.error("Failed to send email to %s: %s", receiver_email, str(e))

