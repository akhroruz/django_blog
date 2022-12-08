from django.core.mail import send_mail

from root.settings import EMAIL_HOST_USER


def send_mail_to(subject, message, receivers):
    send_mail(subject, message, EMAIL_HOST_USER, [receivers],
              fail_silently=False)
