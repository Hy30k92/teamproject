import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

logging.basicConfig(level=logging.INFO)

def send_notification_email(receiver_email: str, approval_link: str, token: str):
    sender_email = "teereal@naver.com"
    sender_password = "WEDVPB9ZUMJF"

    subject = "방문 신청이 완료되었습니다."
    body = f"""방문 신청이 완료되었습니다. 아래 링크를 통해 자신의 방문 상태를 확인할 수 있습니다:
    
    방문 상태 조회 링크: {approval_link}

    아래의 토큰을 이용하여 방문 상태를 조회할 수 있습니다:
    {token}
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.naver.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        logging.info("Email sent successfully to %s", receiver_email)
    except Exception as e:
        logging.error("Failed to send email to %s: %s", receiver_email, str(e))
