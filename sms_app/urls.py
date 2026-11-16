from django.urls import path
from . import views
app_name = "sms_app"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("compose/", views.compose, name="compose"),
    path("history/", views.history, name="history"),
    path("messages/<int:pk>/", views.message_detail, name="message_detail"),
    path("settings/", views.settings_page, name="settings"),
    path("messages/<int:pk>/refresh-status/", views.refresh_status, name="refresh_status"),
]
