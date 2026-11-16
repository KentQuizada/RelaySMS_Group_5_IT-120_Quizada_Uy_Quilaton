from django.contrib import admin
from .models import SMSMessage

@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient_number", "status", "message_sid", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("recipient_number", "message_body", "message_sid")
    readonly_fields = ("created_at", "updated_at")
