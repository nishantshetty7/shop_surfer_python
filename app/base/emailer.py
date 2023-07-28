from django.conf import settings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.template.loader import render_to_string
import datetime
import jwt
import boto3
import json


def generate_verification_token(user_obj):
    secret_key = settings.SECRET_KEY
    # Set the expiration time
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=1)

    # Create the payload
    payload = {
        'exp': expiration_time,
        'sub': user_obj.id,
        'email': user_obj.email,
        'first_name': user_obj.first_name
        # Add additional claims as needed
    }

    # Generate the JWT token
    token = jwt.encode(payload, secret_key, algorithm='HS256')

    return token

def trigger_email_queue(email_data):
    topic_arn = settings.SNS_TOPIC_ARN

    sns_client = boto3.client(
        "sns",
        region_name="ap-south-1",
    )

    message_id = sns_client.publish(
        TopicArn=topic_arn,
        Message=json.dumps(email_data),
    )
    return message_id
    

def send_verification_email(user_obj):
    recipient_email = user_obj.email

    token = generate_verification_token(user_obj)

    # Define the context for the email template
    context = {
        'first_name': user_obj.first_name,
        'verification_url': f'{settings.REACT_APP_URL}/verify/?token={token}'
    }

    # Render the HTML template with the context
    html_content = render_to_string('base/email_verification.html', context)

    email_data = {"recipient_email": recipient_email, "html_content": html_content}
    result = trigger_email_queue(email_data)
    return True
    
    
# def send_verification_email(user_obj):

#     sender_email = settings.SENDER_EMAIL
#     sender_password = settings.GMAIL_APP_PASSWORD
#     recipient_email = user_obj.email

#     # Set up the SMTP server
#     smtp_server = 'smtp.gmail.com'
#     smtp_port = 587

#     # Create a message object
#     message = MIMEMultipart()
#     message['From'] = sender_email
#     message['To'] = recipient_email
#     message['Subject'] = 'Activate Your Account'

#     token = generate_verification_token(user_obj)

#     # Compose the HTML email body
#     # html = f"""
#     # <html>
#     # <head></head>
#     # <body>
#     #     <h1 style="color: gray; text-align: center;">ShopSurfer</h1>
#     #     <p>Hello {user_obj.first_name}! To activate your account, please click on the verification link below:</p>
#     #     <a href="http://localhost:3000/verify/?token={token}" style="background-color:#4CAF50;color:white;padding:12px 20px;text-align:center;
#     #     text-decoration:none;display:inline-block;border-radius:4px;font-weight: bold;">Verify Now</a>
#     # </body>
#     # </html>
#     # """

#     # Define the context for the email template
#     context = {
#         'first_name': user_obj.first_name,
#         'verification_url': f'{settings.REACT_APP_URL}/verify/?token={token}'
#     }

#     # Render the HTML template with the context
#     html_content = render_to_string('base/email_verification.html', context)

#     message.attach(MIMEText(html_content, 'html'))

#     try:
#         # Establish a secure connection with the SMTP server
#         server = smtplib.SMTP(smtp_server, smtp_port)
#         server.starttls()

#         # Log in to the sender's email account
#         server.login(sender_email, sender_password)

#         # Send the email
#         server.sendmail(sender_email, recipient_email, message.as_string())

#         # Close the connection
#         server.quit()
#         print("Verification email sent successfully!")
#         return True
#     except smtplib.SMTPException as e:
#         print("Error: Unable to send email.")
#         print(e)
#         return False

