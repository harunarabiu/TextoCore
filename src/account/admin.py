from django.contrib import admin
from .models import Account, AuthToken

# Register your models here.


class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'book_balance', 'phone')
    list_filter = ('user', 'balance', 'book_balance', 'phone')
    search_fields = ['user__username']


class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'is_active')
    list_filter = ('user', 'token', 'is_active')
    search_fields = ['user__username', 'token', 'is_active']


admin.site.register(Account, AccountAdmin)
admin.site.register(AuthToken, AuthTokenAdmin)
