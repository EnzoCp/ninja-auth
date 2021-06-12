import threading
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class WelcomeMail(threading.Thread):
    def __init__(self, email):
        self.email = email
        self.template_name = settings.NINJA_AUTH_CONFIG.pop("WELCOME_MAIL_TEMPLATE")
        self.subject = settings.NINJA_AUTH_CONFIG.pop("WELCOME_MAIL_SUBJECT")
        threading.Thread.__init__(self)

    def run(self):
        user = get_object_or_404(User, email=self.email)
        if user:
            template = render_to_string(self.template_name)
            send_mail(
                self.subject,
                template,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
                html_message=template
            )


class PasswordResetMail(threading.Thread):
    def __init__(self, user_email):
        self.user_email = user_email
        self.domain = settings.NINJA_AUTH_CONFIG.pop('DOMAIN')
        self.protocol = settings.NINJA_AUTH_CONFIG.pop('PROTOCOL')
        threading.Thread.__init__(self)

    def run(self):
        user = User.objects.get(email=self.user_email)
        email_template_name = 'password_reset_mail.html'
        subject = 'Password Reset Requested'
        context = {
            'domain': self.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "user": user,
            'token': default_token_generator.make_token(user),
            'protocol': self.protocol
        }
        email = render_to_string(email_template_name, context)
        try:
            send_mail(subject, email, settings.EMAIL_HOST_USER, [user.email], html_message=email)
        except BadHeaderError:
            return f'Invalid header found'
            
            
class BaseHtmlMessageEmail(threading.Thread):
    def __init__(self, email, template_name, subject, context: dict = None):
        self.email = email
        self.template_name = template_name
        self.subject = subject
        self.context = context
        threading.Thread.__init__(self)
        
    def run(self):
        template = render_to_string(self.template_name, self.context)
        send_mail(
            self.subject,
            template,
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=False,
            html_message=template
        )
