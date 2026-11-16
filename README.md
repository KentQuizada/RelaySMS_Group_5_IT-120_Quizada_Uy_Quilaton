# RelaySMS — Django SMS Messaging Application (SMSGate Android Gateway)

A student-built IT 120 project for composing and sending SMS through **SMSGate (SMS Gateway for Android)**. Django sends a server-side REST API request to SMSGate Cloud Server; the connected Android phone sends the message using its SIM and mobile carrier.

> **Delivery and cost note:** SMSGate is the gateway software, not a free mobile-network SMS plan. The Android phone needs internet access to stay connected to SMSGate and a SIM/mobile plan that permits outgoing SMS. Carrier charges or bundle limits may apply. An API request accepted/queued by SMSGate is not proof that the recipient received the SMS.

## 1. Features

- Django dashboard with message statistics and recent activity
- SMS composition with E.164 phone-number validation
- Server-side validation and CSRF protection
- SMS submission through the official SMSGate Cloud REST API
- Secure credentials in environment variables (HTTP Basic Authentication)
- SQLite message history, message details, and status refresh
- Search, status filter, and pagination
- Live character counter and message preview
- Settings page that reports configuration presence without revealing secrets
- Automated tests that mock HTTP requests and never send real SMS

## 2. Technology stack

| Technology | Version used | Purpose |
|---|---|---|
| Python | 3.13 (3.12 or newer required) | Programming language |
| Django | 6.0.10 | Web framework |
| SQLite | Bundled with Python | Message history database |
| HTML, CSS, JavaScript | — | User interface, character counter, preview |
| SMSGate (SMS Gateway for Android) | Cloud Server mode | Sends SMS through the Android phone's SIM |
| `requests` | 2.34.2 | HTTP calls to the SMSGate REST API |
| `python-dotenv` | 1.2.4 | Loads credentials from `.env` |
| `phonenumbers` | 9.0.43 | E.164 phone-number validation |

`requirements.txt` was generated with `pip freeze > requirements.txt` and pins every package, including indirect dependencies (`asgiref`, `sqlparse`, `tzdata`, `certifi`, `charset-normalizer`, `idna`, `urllib3`). Django 6.0 requires Python 3.12 or newer.

## 3. Set up SMSGate on Android

1. Install **SMS Gateway for Android** from the official project website: <https://sms-gate.app/>. The project documentation supports Android 5.0 and newer; check current release notes and device compatibility.
2. Open the app and choose **Cloud Server** mode.
3. Start/activate the service and confirm the registration prompt if shown. The app creates or displays the Cloud Server account credentials.
4. In the app's **Cloud Server** settings, locate the generated username and password. Keep them private.
5. Grant the required SMS permissions and select/configure the SIM slot if your phone has multiple SIMs.
6. Keep the phone powered on, connected to the internet, and the SMSGate service running. Disable battery restrictions if Android stops the service in the background.
7. Confirm that the SIM can send SMS and that your carrier plan has sufficient SMS allowance/load.

Official references:
- Website: <https://sms-gate.app/>
- Getting started: <https://docs.sms-gate.app/getting-started/>
- Cloud Server: <https://docs.sms-gate.app/getting-started/cloud-server/>
- API overview: <https://docs.sms-gate.app/integration/api/>
- Authentication: <https://docs.sms-gate.app/integration/authentication/>
- Sending messages: <https://docs.sms-gate.app/features/sending-messages/>
- API explorer: <https://api.sms-gate.app/docs/index.html>

## 4. Install and run on Windows

Open this folder in VS Code. Open **Terminal → New Terminal** and make sure the terminal is in the folder containing `manage.py`.

### Check Python

```powershell
python --version
```

If PowerShell says `python` is not recognized, Python is installed but not on PATH. Use the Windows Python launcher `py` instead (for example `py --version` and `py -m venv .venv`). After the virtual environment is activated, `python` works normally.

### Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Every `python manage.py ...` command must be run from the folder that contains `manage.py`, not from the inner `sms_project` settings folder.

If PowerShell blocks activation, run this in the current terminal and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Create your local environment file

```powershell
Copy-Item .env.example .env
```

Open `.env` and enter your SMSGate Cloud Server credentials:

```env
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

SMSGATE_USERNAME=your_cloud_server_username
SMSGATE_PASSWORD=your_cloud_server_password
SMSGATE_DEVICE_ID=
SMSGATE_SIM_NUMBER=
SMSGATE_BASE_URL=https://api.sms-gate.app
```

- `SMSGATE_USERNAME` and `SMSGATE_PASSWORD` are shown in the Android app's Cloud Server settings.
- `SMSGATE_DEVICE_ID` is optional. Leave blank to let SMSGate route to an eligible connected device. Set it only if you need to target a specific device and have its ID.
- `SMSGATE_SIM_NUMBER` is optional. It is the **SIM slot number** (`1`, `2`, or `3`), **not a phone number**. Leave it blank to use the phone's default SIM. Entering a phone number here makes SMSGate reject every message with HTTP 400; the app now detects this and shows a clear configuration error.
- The SMSGate app's font makes the letter `O` and the digit `0` look almost identical. Copy the password and device ID exactly; if unsure, confirm the device ID with `GET https://api.sms-gate.app/3rdparty/v1/devices` using the same credentials.
- Restart `runserver` after any change to `.env`; the file is read only when the server starts.
- Do not put credentials in Python files, templates, screenshots, or GitHub.
- `.env` is excluded by `.gitignore`; commit `.env.example` only.

### Create database tables and run

```powershell
python manage.py migrate
python manage.py check
python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

## 5. Application pages

| Page | URL | Purpose |
|---|---|---|
| Dashboard | `/` | Statistics and recent activity |
| Compose SMS | `/compose/` | Validate and send a message |
| Message history | `/history/` | Search/filter previous attempts |
| Settings | `/settings/` | Check gateway configuration |
| Django admin | `/admin/` | Manage records (create a superuser first) |

Optional admin account:

```powershell
python manage.py createsuperuser
```

## 6. SMSGate API integration details

This project uses the SMSGate **Cloud Server** API base URL `https://api.sms-gate.app` and the documented endpoint:

`POST /3rdparty/v1/messages`

The request uses HTTP Basic Authentication with the Cloud Server username/password and a JSON body similar to:

```json
{
  "phoneNumbers": ["+639171234567"],
  "textMessage": {"text": "Hello from RelaySMS!"}
}
```

Optional `deviceId` and `simNumber` are included only when configured. A successful API acceptance response (commonly HTTP 202) means SMSGate accepted/queued the message. It does not mean the carrier has delivered it. The app stores the returned message ID and the **Refresh status from SMSGate** action queries `GET /3rdparty/v1/messages/{id}` for its latest status.

SMSGate Cloud Server is a third-party hosted service. For sensitive messages, review the provider's privacy and end-to-end encryption documentation and consider a private deployment. Never use this student project for unsolicited/bulk messaging; follow your carrier's terms and local rules.

## 7. Testing

Automated tests use mocked HTTP requests. They do not contact SMSGate and do not consume SIM load.

```powershell
python manage.py test
```

### Automated test results

Last run: 16 November 2026, Python 3.13.9, Django 6.0.10. **Result: 10 tests, all passed (`OK`).**

| # | Test | What it verifies | Result |
|---|---|---|---|
| 1 | `test_dashboard_loads` | Dashboard page returns HTTP 200 | ✅ Pass |
| 2 | `test_compose_loads` | Compose page returns HTTP 200 | ✅ Pass |
| 3 | `test_empty_fields_rejected` | Blank recipient/message is rejected and nothing is saved | ✅ Pass |
| 4 | `test_invalid_phone_rejected` | Invalid number (`12345`) is rejected and nothing is saved | ✅ Pass |
| 5 | `test_missing_gateway_credentials_saved_as_failed_attempt` | Missing credentials are recorded as a failed attempt with a clear error | ✅ Pass |
| 6 | `test_smsgate_service_sends_expected_request` | Correct SMSGate URL, JSON body, and Basic Auth are used | ✅ Pass |
| 7 | `test_successful_submission_saved_and_redirected` | Accepted message is saved and the user is redirected to details | ✅ Pass |
| 8 | `test_history_and_detail` | History and message detail pages display records | ✅ Pass |
| 9 | `test_refresh_status_updates_record` | Status refresh updates the stored status | ✅ Pass |
| 10 | `test_settings_hides_credentials` | Settings page never displays the username or password | ✅ Pass |

### Manual test procedure

Test the real integration only after configuring SMSGate and an authorized recipient. Send a short message to your own verified/controlled test number first.

| # | Procedure | Expected result | Actual result |
|---|---|---|---|
| 1 | Submit the compose form with both fields empty | Validation errors shown; no SMS sent | ✅ Pass |
| 2 | Enter `09171234567` (local format) | Error asking for E.164 format (`+63...`) | ✅ Pass |
| 3 | Leave `SMSGATE_USERNAME`/`PASSWORD` blank and send | "SMSGate is not configured" error; attempt saved as failed | ✅ Pass |
| 4 | Set `SMSGATE_SIM_NUMBER` to a phone number and send | Clear "must be a SIM slot" error | ✅ Pass (found and fixed during testing) |
| 5 | Send a real SMS with valid configuration | SMSGate accepts (HTTP 202); message appears in history as queued | _Fill in after demo_ |
| 6 | Check the recipient phone | SMS received | _Fill in after demo_ |
| 7 | Click **Refresh status from SMSGate** | Status updates to sent/delivered | _Fill in after demo_ |

## 8. Troubleshooting

- **SMSGate is not configured:** confirm `.env` exists in the same folder as `manage.py`, contains both Cloud Server credentials, and restart `runserver`.
- **401/403:** re-check the username/password shown in the Android app's Cloud Server settings.
- **400:** check the E.164 recipient number, message, Android permissions, device registration, and SIM settings. The most common cause is putting a phone number in `SMSGATE_SIM_NUMBER`; it must be `1`, `2`, `3`, or blank. The error message now includes SMSGate's own explanation.
- **Phone/device unavailable:** open SMSGate on Android, ensure Cloud Server service is running, and verify internet access and battery permissions.
- **No SMS received:** check the phone's sent-message activity, SIM slot, carrier balance/SMS bundle, recipient number, and carrier restrictions. Gateway acceptance is not delivery confirmation.
- **Status unavailable:** some carriers/SIMs do not provide delivery reports; the status may remain queued/sent/unknown.

## 9. GitHub submission

Before pushing, verify that `.env` is not staged:

```powershell
git init
git status
git add .
git status
git commit -m "Initial RelaySMS Django application with SMSGate"
```

Create an empty repository on GitHub, then connect it (replace the URL with your own):

```powershell
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/relay-sms.git
git push -u origin main
```

Never commit `.env`, real credentials, or private recipient information. Group members should make meaningful commits for their contributions.

## 10. Group members and responsibilities

| Member | Responsibilities |
|---|---|
| **Cedric Michael Uy** | Django project setup, views, URLs, and application logic |
| **Mely Kris Quilaton** | User interface, forms, validation, and user feedback |
| **Kent Quizada** | SMS provider integration (SMSGate), testing, documentation, and demonstration |

All members understand the complete workflow and can explain it.

## 11. Demonstration checklist

1. Introduce RelaySMS and its purpose.
2. Show the dashboard and compose form.
3. Demonstrate empty-field and invalid-number validation.
4. Enter an authorized test number and send a real SMS.
5. Show the recipient phone receiving the message, if delivery succeeds.
6. Show the saved history and message details.
7. Refresh status and explain that queued/accepted is not the same as delivered.
8. Explain Django, SMSGate REST API, Android phone/SIM, SQLite, and environment-variable security.
9. Explain each group member's contribution.

Keep the video between 3 and 10 minutes. Hide usernames/passwords and other secrets.

## 12. Known limitations

- A real SMS requires a working Android device, internet connectivity, SMS permissions, a functioning SIM, and a carrier plan that allows sending.
- Carrier charges, SMS bundles, network coverage, device battery management, and delivery reports are outside Django's control.
- The public Cloud Server mode sends API requests through a hosted service; review its privacy model before using sensitive content.
- The local development server is not publicly reachable for inbound webhooks without a secure public endpoint. This version uses manual status refresh instead.
- SMS status names and provider responses can vary by SMSGate/API version; verify behavior against the API explorer for the installed version.

## 13. Assignment alignment

This project addresses the IT 120 requirements for a Django application, external SMS gateway API integration, input validation, understandable error handling, secure credential configuration, message history as an additional feature, tests, GitHub readiness, README documentation, and demonstration preparation. Actual SMS sending still needs to be verified on the group's own Android phone and SIM before submission.
