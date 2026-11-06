from django.urls import path

from . import views


app_name = "system_settings"


urlpatterns = [
    path("", views.settings_home, name="home"),
    path("general/", views.general_settings, name="general"),
    path("security/", views.security_settings, name="security"),
    path("access-control/", views.access_control_settings, name="access_control"),
    path("biometric/", views.biometric_settings, name="biometric"),
    path("devices/", views.device_settings, name="devices"),
    path("notifications/", views.notification_settings, name="notifications"),
]