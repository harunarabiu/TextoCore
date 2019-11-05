from django.contrib import admin
from .models import Account, AuthToken, User, Country, Verification
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
# Register your models here.


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('first_name', 'last_name', 'email',
                    'is_admin', 'is_staff', 'is_active')
    list_filter = ('is_admin', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Account Status', {'fields': ('is_active',)}),
        ('Permissions', {'fields': ('is_admin', 'is_staff',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email',  'password1', 'first_name', 'last_name', 'is_admin', 'is_staff',)}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'book_balance', 'phone', 'country')
    list_filter = ('country',)
    search_fields = ['user__email']


class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'is_active')
    list_filter = ('user', 'token', 'is_active')
    search_fields = ['user__username', 'token', 'is_active']


class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'CCC', 'is_active')
    list_filter = ('is_active',)
    search_fields = ['name', 'CCC']


class VerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'phone_token', 'email', 'email_token')
    search_fields = ['phone_token', 'email_token']


admin.site.register(Account, AccountAdmin)
admin.site.register(AuthToken, AuthTokenAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Verification, VerificationAdmin)
admin.site.unregister(Group)
