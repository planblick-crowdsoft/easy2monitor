import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import boto3

def msg_handler(ch, method=None, properties=None, body=None):
    try:
        payload = body.decode()
        payload = json.loads(payload)

        if method.routing_key == "http_check_failed":
            subject = f"HTTP Check FAILED for {payload.get('check_name')}"

        if method.routing_key == "http_check_recovered":
            subject = f"HTTP Check RECOVERED for {payload.get('check_name')}"


        if os.getenv("SEND_SMS") == "1":
            # Create an SNS client
            client = boto3.client(
                "sns",
                region_name=os.getenv("AWS_REGION"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
                aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
            )

            # Create the topic if it doesn't exist (this is idempotent)
            topic = client.create_topic(Name="notifications")
            topic_arn = topic['TopicArn']  # get its Amazon Resource Name

            # Add SMS Subscribers
            for number in json.loads(os.getenv("SMS_RECIPIENTS")):
                print("Sending sms to", number)
                client.subscribe(
                    TopicArn=topic_arn,
                    Protocol='sms',
                    Endpoint=number  # <-- number who'll receive an SMS message.
                )

            # Publish a message.
            client.publish(Message=subject, TopicArn=topic_arn)



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
        print(e)
        ch.basic_nack(method.delivery_tag)
