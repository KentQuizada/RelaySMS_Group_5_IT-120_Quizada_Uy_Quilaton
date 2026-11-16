from unittest.mock import Mock, patch
from django.test import TestCase, override_settings
from django.urls import reverse
from .models import SMSMessage

class SMSApplicationTests(TestCase):
    def test_dashboard_loads(self):
        self.assertEqual(self.client.get(reverse("sms_app:dashboard")).status_code, 200)

    def test_compose_loads(self):
        self.assertEqual(self.client.get(reverse("sms_app:compose")).status_code, 200)

    def test_empty_fields_rejected(self):
        response = self.client.post(reverse("sms_app:compose"), {"recipient_number": "", "message_body": ""})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SMSMessage.objects.exists())

    def test_invalid_phone_rejected(self):
        response = self.client.post(reverse("sms_app:compose"), {"recipient_number": "12345", "message_body": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SMSMessage.objects.exists())

    @override_settings(SMSGATE_USERNAME="", SMSGATE_PASSWORD="")
    def test_missing_gateway_credentials_saved_as_failed_attempt(self):
        response = self.client.post(reverse("sms_app:compose"), {"recipient_number": "+639171234567", "message_body": "Test"})
        self.assertEqual(response.status_code, 200)
        record = SMSMessage.objects.get()
        self.assertEqual(record.status, SMSMessage.Status.FAILED)
        self.assertIn("not configured", record.error_message)

    @patch("sms_app.services.requests.post")
    @override_settings(SMSGATE_USERNAME="demo", SMSGATE_PASSWORD="secret", SMSGATE_BASE_URL="https://api.sms-gate.app", SMSGATE_DEVICE_ID="", SMSGATE_SIM_NUMBER="")
    def test_smsgate_service_sends_expected_request(self, mocked_post):
        from .services import send_sms
        mocked_response = Mock(status_code=202, content=b'{"id":"msg-123","status":"pending"}')
        mocked_response.json.return_value = {"id": "msg-123", "status": "pending"}
        mocked_post.return_value = mocked_response
        result = send_sms("+639171234567", "Hello")
        self.assertEqual(result["sid"], "msg-123")
        self.assertEqual(result["status"], "pending")
        self.assertEqual(mocked_post.call_args.args[0], "https://api.sms-gate.app/3rdparty/v1/messages")
        self.assertEqual(mocked_post.call_args.kwargs["json"], {"phoneNumbers": ["+639171234567"], "textMessage": {"text": "Hello"}})
        self.assertEqual(mocked_post.call_args.kwargs["auth"].username, "demo")

    @patch("sms_app.views.send_sms")
    @override_settings(SMSGATE_USERNAME="demo", SMSGATE_PASSWORD="secret")
    def test_successful_submission_saved_and_redirected(self, mocked_send):
        mocked_send.return_value = {"sid": "msg-123", "status": "pending", "warning": ""}
        response = self.client.post(reverse("sms_app:compose"), {"recipient_number": "+639171234567", "message_body": "Hello"})
        self.assertEqual(response.status_code, 302)
        record = SMSMessage.objects.get()
        self.assertEqual(record.message_sid, "msg-123")
        self.assertEqual(record.status, SMSMessage.Status.QUEUED)
        mocked_send.assert_called_once()

    def test_history_and_detail(self):
        record = SMSMessage.objects.create(recipient_number="+639171234567", message_body="Hello")
        self.assertEqual(self.client.get(reverse("sms_app:history")).status_code, 200)
        self.assertEqual(self.client.get(reverse("sms_app:message_detail", args=[record.pk])).status_code, 200)

    def test_settings_hides_credentials(self):
        response = self.client.get(reverse("sms_app:settings"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "SMSGATE_PASSWORD=")

    @patch("sms_app.views.refresh_sms_status")
    def test_refresh_status_updates_record(self, mocked_refresh):
        record = SMSMessage.objects.create(recipient_number="+639171234567", message_body="Hello", message_sid="msg-123")
        mocked_refresh.return_value = "delivered"
        response = self.client.post(reverse("sms_app:refresh_status", args=[record.pk]))
        self.assertEqual(response.status_code, 302)
        record.refresh_from_db()
        self.assertEqual(record.status, SMSMessage.Status.DELIVERED)
