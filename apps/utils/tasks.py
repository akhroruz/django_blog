from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.models import User
from apps.utils.token import account_activation_token
from root.settings import EMAIL_HOST_USER


@shared_task
def send_to_gmail(email, domain, type_mail='activate'):
    print('ACCEPT TASK')
    user = User.objects.filter(email=email).first()
    context = {
        'user': user,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(str(user.pk))),
        'token': account_activation_token.make_token(user),
    }

    subject = 'Activate your account'
    template = 'email_activation.html'
    if type_mail == 'reset':
        subject = 'Trouble signing in?'
        template = 'reset_password.html'
    elif type_mail == 'change':
        subject = ''
    else:
        context['username'] = user.username
    message = render_to_string(f'apps/auth/email/{template}', context)


    recipient_list = [email]
    email = EmailMessage(subject, message, EMAIL_HOST_USER, recipient_list)
    email.content_subtype = 'html'
    result = email.send()
    print('Send to MAIL')
    return result


# @shared_task
# def set_reset_to_gmail(email, domain, type):
#     user = User.objects.filter(email=email)
#     subject = 'Reset password'
#     message = render_to_string('apps/auth/forgot_password.html', {
#         'domain': domain,
#         'uid': urlsafe_base64_encode(force_bytes(str(user.pk))),
#         'token': account_activation_token.make_token(user),
#     })

# recipient_list = [email]
# email = EmailMessage(subject, message, EMAIL_HOST_USER, recipient_list)
# email.content_subtype = 'html'
# result = email.send()
# print('Send to MAIL')
# return result

@shared_task
def send_message_to_gmail(email):
    subject = 'Thanks for your invitation!'
    message = 'Your offer has been reviewed.'
    from_email = EMAIL_HOST_USER
    recipient_list = [email]
    print(subject, message, from_email, recipient_list)
    result = send_mail(subject, message, from_email, recipient_list)
    return result
