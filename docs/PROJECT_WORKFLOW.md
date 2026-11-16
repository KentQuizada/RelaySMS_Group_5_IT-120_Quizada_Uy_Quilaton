# RelaySMS Project Workflow

1. User opens the Django dashboard.
2. User enters a recipient in international E.164 format and composes an SMS.
3. Django validates the form server-side and creates an SMSMessage attempt record.
4. The backend reads SMSGate Cloud Server credentials from environment variables.
5. Django submits `POST /3rdparty/v1/messages` to `https://api.sms-gate.app` using HTTP Basic Authentication and the documented JSON request shape.
6. SMSGate routes the request to the connected Android device. The Android app uses the selected SIM and mobile carrier to send the SMS.
7. Django records the provider message ID and initial status. API acceptance is not delivery confirmation.
8. User can request a status refresh; Django calls `GET /3rdparty/v1/messages/{id}` and updates the stored provider status.

## Security notes

- Keep SMSGate Cloud Server username/password in local `.env` only.
- `.env` is excluded from Git. Commit `.env.example` with empty placeholders only.
- Keep API calls on the Django server; never expose credentials in JavaScript or HTML.
- Use authorized recipients and follow carrier rules.

## Test notes

Automated tests mock HTTP requests. They do not send real SMS. A separate manual test with a configured Android phone and authorized recipient is required to verify the live gateway.
