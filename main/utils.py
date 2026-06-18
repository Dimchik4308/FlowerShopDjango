from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.auth import get_user_model
UserModel = get_user_model()
def verify(request,user):
    current_site = get_current_site(request)
    user_pk_bytes = force_bytes(UserModel._meta.pk.value_to_string(user))
    context = {
        "uid": urlsafe_base64_encode(user_pk_bytes),
        "user": user,
        "token": token_generator.make_token(user),
        "domain": current_site.domain,
    }
    message= render_to_string('main/verify_email.html',context=context)
    email = EmailMessage(
        'Verify email',
        message,
        to=[user.email],
    )
    email.send()