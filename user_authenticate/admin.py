from django.contrib import admin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from user_authenticate.models import (User, Key)
from user_authenticate.forms import (UserChangeForm, UserCreationForm)
# Register your models here.


class UserAdmin(BaseUserAdmin):
    change_user_password_template = None
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = [field.name for field in User._meta.fields]

    list_filter = ('is_staff', 'is_active', 'is_superuser')
    fieldsets = (
        ('General', {'fields': ('email', 'password', 'phone')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'birthDate', 'img', 'date_joined', 'last_login')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active', 'user_permissions', 'groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
         ),
    )
    ordering = ('email',)


class KeyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Key._meta.fields]


admin.site.register(User, UserAdmin)

admin.site.register(Key, KeyAdmin)
