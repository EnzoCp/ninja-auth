from django.contrib import admin
from .models import AuthToken
from django.contrib.auth.models import User

admin.site.unregister(User)


class AuthokenInlineAdmin(admin.TabularInline):
    model = AuthToken
    max_num = 1


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User
    exclude = ('user_permissions', 'groups', 'last_login', 'date_joined', 'first_name', 'last_name')
    inlines = [AuthokenInlineAdmin]


