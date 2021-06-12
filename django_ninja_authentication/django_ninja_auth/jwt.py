import jwt
from django.conf import settings
from datetime import datetime as dt, timedelta
from jwt import PyJWTError
from .models import AuthToken, get_expire_date
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .schemas import TokenPayload
import pytz
import datetime

ALGORITHM = 'HS256'
User = get_user_model()


def create_access_token(*, data: dict):
    u_id = data['user_id']
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    user = get_object_or_404(User, id=u_id)
    authtoken = AuthToken.objects.create(user=user, token=encoded_jwt)


def create_token(user_id: int):
    return create_access_token(data={"user_id": user_id})


def get_current_user(token: str):
    utc = pytz.UTC
    try:
        authtoken = AuthToken.objects.get(token=token)
        if authtoken.valid_until.replace(tzinfo=utc) >= dt.now(utc):
            user = authtoken.user
            return user
        return None
    except PyJWTError:
        return None

