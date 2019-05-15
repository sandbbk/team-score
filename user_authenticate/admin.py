from django.contrib import admin
from user_authenticate.models import (User, Key)
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in User._meta.fields]


class KeyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Key._meta.fields]


admin.site.register(User, UserAdmin)

admin.site.register(Key, KeyAdmin)
