from django import forms
import phonenumbers
from phonenumbers import NumberParseException

class SMSComposeForm(forms.Form):
    recipient_number = forms.CharField(
        label="Recipient phone number", max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "+639XXXXXXXXX", "autocomplete": "tel", "class": "form-control"}),
        help_text="Use international E.164 format, for example +639XXXXXXXXX.",
    )
    message_body = forms.CharField(
        label="Message", max_length=1600,
        widget=forms.Textarea(attrs={"rows": 6, "placeholder": "Type your message here...", "class": "form-control", "maxlength": "1600"}),
    )

    def clean_recipient_number(self):
        raw = self.cleaned_data["recipient_number"].strip()
        try:
            parsed = phonenumbers.parse(raw, None)
        except NumberParseException:
            raise forms.ValidationError("Enter a valid international phone number, including country code (e.g. +639XXXXXXXXX).")
        if not raw.startswith("+") or not phonenumbers.is_possible_number(parsed) or not phonenumbers.is_valid_number(parsed):
            raise forms.ValidationError("Enter a valid phone number in E.164 format, such as +639XXXXXXXXX.")
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

    def clean_message_body(self):
        message = self.cleaned_data["message_body"].strip()
        if not message:
            raise forms.ValidationError("Please write a message before sending.")
        if len(message) > 1600:
            raise forms.ValidationError("Message cannot exceed 1,600 characters.")
        return message
