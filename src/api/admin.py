from django.contrib import admin
from .models import Message, Response
# Register your models here.


class MessageAdmin(admin.ModelAdmin):
    list_display = ('msg_user', 'msg_sender', 'msg_message', 'msg_destination',
                    'msg_cost', 'msg_status', 'msg_channel', 'msg_schedule', 'created_at')
    list_filter = ('msg_user', 'msg_sender', 'msg_status', 'msg_channel')
    search_fields = ['msg_user__username',
                     'msg_sender', 'msg_message', 'msg_destination']


class ResponseAdmin(admin.ModelAdmin):
    list_display = ('message', 'phone_number', 'msg_id', 'response_code')
    list_filter = ('message', 'phone_number', 'msg_id', 'response_code')
    search_fields = ['phone_number']


admin.site.register(Message, MessageAdmin)
admin.site.register(Response, ResponseAdmin)
