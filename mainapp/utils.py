from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_email(subject, to_email, message, html_message=None, from_email=None):
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=from_email,
        to=[to_email],
    )

    if html_message:
        email.attach_alternative(html_message, "text/html")

    try:
        email.send()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False