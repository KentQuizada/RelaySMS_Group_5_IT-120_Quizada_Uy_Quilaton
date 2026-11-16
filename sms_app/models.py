from django.db import models

class SMSMessage(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        QUEUED = "queued", "Queued"
        SENDING = "sending", "Sending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"
        UNDELIVERED = "undelivered", "Undelivered"
        UNKNOWN = "unknown", "Unknown"

    recipient_number = models.CharField(max_length=20)
    message_body = models.TextField()
    message_sid = models.CharField(max_length=64, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    error_message = models.CharField(max_length=500, blank=True)
    provider_status = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient_number} — {self.get_status_display()}"
