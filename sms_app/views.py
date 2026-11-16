import logging
from urllib.parse import urlencode
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from .forms import SMSComposeForm
from .models import SMSMessage
from .services import send_sms, refresh_sms_status, SMSConfigurationError, SMSSendingError, SMSStatusError

logger = logging.getLogger(__name__)

STATUS_MAP = {"pending": "queued", "queued": "queued", "processing": "sending", "sending": "sending", "sent": "sent", "delivered": "delivered", "failed": "failed", "undelivered": "undelivered", "unknown": "unknown"}

def dashboard(request):
    total = SMSMessage.objects.count()
    successful = SMSMessage.objects.filter(status__in=["queued", "sending", "sent", "delivered"]).count()
    failed = SMSMessage.objects.filter(status__in=["failed", "undelivered"]).count()
    recent = SMSMessage.objects.all()[:6]
    return render(request, "sms_app/dashboard.html", {"total": total, "successful": successful, "failed": failed, "recent": recent})

def compose(request):
    if request.method == "POST":
        form = SMSComposeForm(request.POST)
        if form.is_valid():
            record = SMSMessage.objects.create(
                recipient_number=form.cleaned_data["recipient_number"],
                message_body=form.cleaned_data["message_body"], status=SMSMessage.Status.PENDING,
            )
            try:
                result = send_sms(record.recipient_number, record.message_body)
                record.message_sid = result["sid"]
                record.provider_status = result["status"]
                record.status = STATUS_MAP.get(result["status"], "queued")
                record.save(update_fields=["message_sid", "provider_status", "status", "updated_at"])
                messages.success(request, "SMSGate accepted the SMS request. This is not delivery confirmation; refresh the status later.")
                return redirect("sms_app:message_detail", pk=record.pk)
            except SMSConfigurationError as exc:
                record.status = SMSMessage.Status.FAILED
                record.error_message = str(exc)
                record.save(update_fields=["status", "error_message", "updated_at"])
                messages.error(request, str(exc))
            except SMSSendingError as exc:
                record.status = SMSMessage.Status.FAILED
                record.error_message = str(exc)
                record.save(update_fields=["status", "error_message", "updated_at"])
                logger.warning("SMS submission failed for record %s: %s", record.pk, exc)
                messages.error(request, str(exc))
        else:
            messages.error(request, "Please correct the highlighted fields.")
    else:
        form = SMSComposeForm()
    return render(request, "sms_app/compose.html", {"form": form})

def history(request):
    qs = SMSMessage.objects.all()
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    if query:
        qs = qs.filter(Q(recipient_number__icontains=query) | Q(message_body__icontains=query) | Q(message_sid__icontains=query))
    valid_statuses = {choice[0] for choice in SMSMessage.Status.choices}
    if status in valid_statuses:
        qs = qs.filter(status=status)
    page_obj = Paginator(qs, 10).get_page(request.GET.get("page"))
    return render(request, "sms_app/history.html", {"page_obj": page_obj, "query": query, "selected_status": status, "statuses": SMSMessage.Status.choices})

def message_detail(request, pk):
    record = get_object_or_404(SMSMessage, pk=pk)
    return render(request, "sms_app/message_detail.html", {"record": record})

def settings_page(request):
    return render(request, "sms_app/settings.html", {
        "username_configured": bool(settings.SMSGATE_USERNAME),
        "password_configured": bool(settings.SMSGATE_PASSWORD),
        "device_configured": bool(settings.SMSGATE_DEVICE_ID),
        "sim_configured": bool(settings.SMSGATE_SIM_NUMBER),
        "base_url": settings.SMSGATE_BASE_URL,
    })

@require_POST
def refresh_status(request, pk):
    record = get_object_or_404(SMSMessage, pk=pk)
    if not record.message_sid:
        messages.warning(request, "This submission has no SMSGate message ID, so its status cannot be refreshed from the API.")
        return redirect("sms_app:message_detail", pk=record.pk)
    try:
        provider_status = refresh_sms_status(record.message_sid, record.recipient_number)
        record.provider_status = provider_status
        record.status = STATUS_MAP.get(provider_status, "unknown")
        if provider_status == "failed":
            record.error_message = "SMSGate reports that this message failed. Check the SMSGate dashboard and your Android device."
        record.save(update_fields=["provider_status", "status", "error_message", "updated_at"])
        messages.success(request, f"Message status refreshed: {provider_status.title()}.")
    except (SMSConfigurationError, SMSStatusError) as exc:
        messages.error(request, str(exc))
    return redirect("sms_app:message_detail", pk=record.pk)
