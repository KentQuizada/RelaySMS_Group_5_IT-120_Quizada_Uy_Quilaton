from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name="SMSMessage", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("recipient_number", models.CharField(max_length=20)),
        ("message_body", models.TextField()),
        ("message_sid", models.CharField(blank=True, db_index=True, max_length=64)),
        ("status", models.CharField(choices=[("pending", "Pending"), ("queued", "Queued"), ("sending", "Sending"), ("sent", "Sent"), ("delivered", "Delivered"), ("failed", "Failed"), ("undelivered", "Undelivered"), ("unknown", "Unknown")], db_index=True, default="pending", max_length=20)),
        ("error_message", models.CharField(blank=True, max_length=500)),
        ("provider_status", models.CharField(blank=True, max_length=40)),
        ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
    ], options={"ordering": ["-created_at"]})]
