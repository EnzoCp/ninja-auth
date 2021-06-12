import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from ninja import Schema
from ninja.errors import ValidationError
from ninja.orm import create_schema
from pydantic import root_validator

User = get_user_model()

username = settings.NINJA_AUTH_CONFIG.pop('USERNAME_FIELD')

def get_username_field():
    if 'USERNAME_FIELD' in settings.NINJA_AUTH_CONFIG:
        return settings.NINJA_AUTH_CONFIG.pop('USERNAME_FIELD')
    else:
        return 'username'


class TokenPayload(Schema):
    user_id: int


class Message(Schema):
    message: str


class LoginOutSchema(Schema):
    type: str
    token: str
    valid_until: datetime.datetime


class LoginSchema(Schema):
    username: str
    password: str


class RefreshToken(Schema):
    token: str


class ForgotMyPassword(Schema):
    email: str


class PasswordChange(Schema):
    old_password: str
    new_password: str