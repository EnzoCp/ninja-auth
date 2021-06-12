from ninja.security import HttpBearer
from django_ninja_auth.jwt import get_current_user


class LoggedIn(HttpBearer):
    def authenticate(self, request, token: str):
        user = get_current_user(token)
        if user:
            return user


class IsAdmin(HttpBearer):
    def authenticate(self, request, token: str):
        user = get_current_user(token)
        if user and user.is_superuser:
            return user