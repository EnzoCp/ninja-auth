from ninja.errors import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

def username_is_inexistent(cls, v):
    if not v:
        raise ValidationError({"username": ("Nome de usuario e obrigatorio")})
    if User.objects.filter(username=v).exists():
        raise ValidationError({"username": ("Nome de usuario ja cadastrado")})
    return v


def email_is_inexistent(cls, v):
    if not v:
        raise ValidationError({"email": ("Email e obrigatorio")})
    if User.objects.filter(email=v.strip()).exists():
        raise ValidationError({"email": ("Email ja esta em uso")})
    return v


def passwords_match(cls, v, values, **kwargs):
    if 'password1' in values and v != values['password1']:
        raise ValidationError({'password1': ('As senhas nao coincidem')})
    return v