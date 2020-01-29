import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json


def msg_handler(ch, method=None, properties=None, body=None):
    try:
        payload = body.decode()
        payload = json.loads(payload)

        if method.routing_key == "http_check_failed":
            subject = f"HTTP Check FAILED for {payload.get('check_name')}"

        if method.routing_key == "http_check_recovered":
            subject = f"HTTP Check RECOVERED for {payload.get('check_name')}"

        if os.getenv("SEND_MAIL") == "1":
            s = smtplib.SMTP(host=os.getenv("SMTP_HOST"), port=os.getenv("SMTP_PORT"))
            s.starttls()
            s.login(os.getenv("SMTP_LOGIN"), os.getenv("SMTP_PASSWORD"))
            msg = MIMEMultipart()  # create a message

            # setup the parameters of the message
            msg['From'] = os.getenv("MAIL_SENDER")
            msg['To'] = os.getenv("MAIL_RECIPIENT")
            msg['Subject'] = subject

            # add in the message body
            msg.attach(MIMEText(json.dumps(payload, sort_keys=True, indent=4), 'plain'))

            # send the message via the server set up earlier.
            s.send_message(msg)

        ch.basic_ack(method.delivery_tag)
    except Exception as e:
        ch.basic_nack(method.delivery_tag)
