"""SMSGate Android gateway integration (Cloud Server API)."""
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings

class SMSConfigurationError(Exception):
    """Raised when SMSGate settings are incomplete."""

class SMSSendingError(Exception):
    """Raised when SMSGate rejects a request or cannot be reached."""

class SMSStatusError(Exception):
    """Raised when message status cannot be retrieved."""


def _credentials():
    username = settings.SMSGATE_USERNAME
    password = settings.SMSGATE_PASSWORD
    if not username or not password:
        raise SMSConfigurationError(
            "SMSGate is not configured. Add SMSGATE_USERNAME and SMSGATE_PASSWORD from your Android app's Cloud Server settings to .env."
        )
    return HTTPBasicAuth(username, password)


def _url(path):
    return f"{settings.SMSGATE_BASE_URL}{path}"


def _provider_detail(response):
    """Extract SMSGate's own error message (no credentials are ever included)."""
    try:
        data = response.json()
        if isinstance(data, dict):
            return str(data.get("message") or data.get("error") or "")[:300]
    except ValueError:
        pass
    return response.text[:300] if response.text else ""


def _safe_error(status_code, detail=""):
    suffix = f" SMSGate said: {detail}" if detail else ""
    if status_code in (401, 403):
        return "SMSGate authentication failed. Check the Cloud Server username and password in .env." + suffix
    if status_code == 429:
        return "SMSGate or your device is rate-limiting requests. Wait and try again." + suffix
    if status_code == 400:
        return "SMSGate rejected the request. Check the recipient number, message, device connection, and SIM configuration." + suffix
    return f"SMSGate returned an error (HTTP {status_code}). Check the Android app and gateway dashboard." + suffix


def _sim_number():
    raw = settings.SMSGATE_SIM_NUMBER
    if not raw:
        return None
    if not raw.isdigit() or not 1 <= int(raw) <= 3:
        raise SMSConfigurationError(
            f"SMSGATE_SIM_NUMBER must be a SIM slot (1, 2 or 3), not a phone number. Current value: {raw!r}. "
            "Leave it blank to use the phone's default SIM."
        )
    return int(raw)


def send_sms(recipient: str, body: str):
    """Queue an SMS through SMSGate Cloud Server. A 202 means accepted, not delivered."""
    payload = {"phoneNumbers": [recipient], "textMessage": {"text": body}}
    if settings.SMSGATE_DEVICE_ID:
        payload["deviceId"] = settings.SMSGATE_DEVICE_ID
    sim = _sim_number()
    if sim:
        payload["simNumber"] = sim
    try:
        response = requests.post(
            _url("/3rdparty/v1/messages"), auth=_credentials(), json=payload,
            headers={"Content-Type": "application/json"}, timeout=30,
        )
        if response.status_code not in (200, 201, 202):
            raise SMSSendingError(_safe_error(response.status_code, _provider_detail(response)))
        data = response.json() if response.content else {}
        message_id = data.get("id") or data.get("messageId") or data.get("message_id") or ""
        provider_status = (data.get("status") or "queued").lower()
        return {"sid": str(message_id), "status": provider_status, "warning": ""}
    except SMSConfigurationError:
        raise
    except SMSSendingError:
        raise
    except requests.Timeout as exc:
        raise SMSSendingError("The SMSGate request timed out. Check your internet connection and Android gateway status.") from exc
    except requests.RequestException as exc:
        raise SMSSendingError("Could not connect to SMSGate. Check your internet connection and Cloud Server mode.") from exc
    except (ValueError, TypeError) as exc:
        raise SMSSendingError("SMSGate returned an unexpected response. Check the gateway dashboard.") from exc


def refresh_sms_status(message_id: str, recipient: str = ""):
    """Retrieve the current status for one SMSGate message."""
    try:
        response = requests.get(
            _url(f"/3rdparty/v1/messages/{message_id}"), auth=_credentials(), timeout=20,
        )
        if response.status_code != 200:
            raise SMSStatusError(f"SMSGate status lookup failed (HTTP {response.status_code}).")
        data = response.json()
        # API versions may wrap the resource in a `data` property.
        if isinstance(data, dict) and isinstance(data.get("data"), dict):
            data = data["data"]
        return str(data.get("status") or "unknown").lower()
    except SMSConfigurationError:
        raise
    except SMSStatusError:
        raise
    except requests.RequestException as exc:
        raise SMSStatusError("Could not connect to SMSGate to refresh the message status.") from exc
    except (ValueError, TypeError, AttributeError) as exc:
        raise SMSStatusError("SMSGate returned an unexpected status response.") from exc
