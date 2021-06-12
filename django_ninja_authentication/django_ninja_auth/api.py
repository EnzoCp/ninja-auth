from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from ninja import Router, Form
from ninja.errors import ValidationError
from .jwt import create_token
from .models import AuthToken
from .schemas import Message, LoginOutSchema, LoginSchema, RefreshToken, ForgotMyPassword
from django.conf import settings
from .utils import WelcomeMail, PasswordResetMail

User = get_user_model()
SIGNUP_SCHEMA = settings.NINJA_AUTH_CONFIG.pop('SIGNUP_SCHEMA')
WELCOME_MAIL_TEMPLATE = settings.NINJA_AUTH_CONFIG.pop('WELCOME_MAIL_TEMPLATE')

router = Router(tags=['Authentication'])


@router.post('/signup/', response={201: Message, 422: Message})
def signup(request, payload: SIGNUP_SCHEMA):
    try:
        user = User.objects.create_user(username=payload.username, password=payload.password1)
        token = create_token(user.id)
        WelcomeMail(user.email, ).start()
        return 201, {'message': "User Created"}
    except ValidationError as e:
        return e


@router.post('/login/', response={200: LoginOutSchema, 422: Message})
def login(request, payload: LoginSchema):
    user = User.objects.get(**{User.USERNAME_FIELD: payload.username})
    if user:
        if check_password(payload.password, user.password):
            token = AuthToken.objects.get(user=user)
            return 200, {'type': 'Bearer', 'token': token.token, 'valid_until': token.valid_until}
        return 422, {'message': 'Wrong Password'}
    return 422, {'message': 'Field Incorrect'}


@router.post('/refresh-token/', response={200: LoginOutSchema, 422: Message})
def refresh_token(request, old_token: RefreshToken):
    token = AuthToken.objects.get(token=old_token.token)
    user = User.objects.get(id=token.user.id)
    token.delete()
    create_token(user.id)
    new_token = AuthToken.objects.get(user=user)
    return 200, {'type': 'Bearer', 'token': new_token.token, 'valid_until': new_token.valid_until}


@router.post('/forgotmypassword/', response={200: Message, 422: Message})
def forgot_my_password(request, payload: ForgotMyPassword):
    if User.objects.filter(email=payload.email).exists():
        PasswordResetMail(payload.email).start()
        return 200, {'message': 'Email sent'}
    else:
        return 422, {'message': 'Invalid email'}


@router.post('/reset/{uidb64}/{token}/', response={422: Message, 200: Message})
def reset_password(request, uidb64, token, password: str = Form(...)):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        return 422, {'message': e}
    if user is not None and default_token_generator.check_token(user, token):
        user.set_password(password)
        user.save()
        return 200, {'message': 'Password Changed'}

