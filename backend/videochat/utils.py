from django.core.mail import send_mail
from django.conf import settings

def send_email(to_email, subject, message, html_message=None):
    try:
        send_mail(
            subject,  # Email subject
            message,  # Plain text message
            settings.EMAIL_HOST_USER,  # From email
            [to_email],  # Recipient list
            fail_silently=False,  # Set to False to raise exceptions if email fails
            html_message=html_message  # Optional HTML version of the email
        )
        print(f"Email sent to {to_email}")  # Debugging log (optional)
    except Exception as e:
        print(f"Error sending email: {str(e)}")  # Debugging log
