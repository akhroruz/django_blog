from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.models import User
from apps.utils.token import account_activation_token
from root.settings import EMAIL_HOST_USER


@shared_task
def send_to_gmail(email, domain, type):
    print('ACCEPT TASK')
    user = User.objects.get(email=email)
    subject = 'Activate your account'
    message = render_to_string('apps/auth/activation-account.html', {
        'user': user,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(str(user.pk))),
        'token': account_activation_token.make_token(user),
        'type': type
    })

    from_email = EMAIL_HOST_USER
    recipient_list = [email]

    result = send_mail(subject, message, from_email, recipient_list)
    print('Send to MAIL')
    return result
