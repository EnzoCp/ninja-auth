from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from datetime import datetime, timedelta

User = get_user_model()


def get_expire_date():
    if 'ACCESS_TOKEN_EXPIRE_MINUTES' in settings.NINJA_AUTH_CONFIG:
        EXPIRE = settings.NINJA_AUTH_CONFIG.pop('ACCESS_TOKEN_EXPIRE_MINUTES')
        return {'type': 'minutes', 'time': EXPIRE}
    elif 'ACCESS_TOKEN_EXPIRE_HOURS' in settings.NINJA_AUTH_CONFIG:
        EXPIRE = settings.NINJA_AUTH_CONFIG.pop('ACCESS_TOKEN_EXPIRE_HOURS')
        return {'type': 'hours', 'time': EXPIRE}
    elif 'ACCESS_TOKEN_EXPIRE_DAYS' in settings.NINJA_AUTH_CONFIG:
        EXPIRE = settings.NINJA_AUTH_CONFIG.pop('ACCESS_TOKEN_EXPIRE_DAYS')
        return {'type': 'days', 'time': EXPIRE}
    else:
        EXPIRE = 1
        return {'type': 'days', 'time': EXPIRE}


class AuthToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=256)
    valid_until = models.DateTimeField()

    def save(self, *args, **kwargs):
        time = get_expire_date()
        type = time.pop("type")
        time_amount = time.pop("time")
        if type == 'minutes':
            self.valid_until = datetime.now() + timedelta(minutes=time_amount)
        elif type == 'hours':
            self.valid_until = datetime.now() + timedelta(hours=time_amount)
        elif type == 'days':
            self.valid_until = datetime.now() + timedelta(days=time_amount)
        super(AuthToken, self).save(*args, **kwargs)
