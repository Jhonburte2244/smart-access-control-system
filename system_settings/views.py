
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import (
    SystemSetting,
    SecuritySetting,
    AccessControlSetting,
    BiometricSetting,
    DeviceSetting,
)


@login_required
def settings_home(request):
    return render(
        request,
        "system_settings/home.html",
    )


@login_required
def general_settings(request):

    settings, created = SystemSetting.objects.get_or_create(
        pk=1,
        defaults={
            "system_name": "Smart Access Control System",
            "system_code": "SMAC",
            "organization": "",
            "location": "",
            "timezone": "Africa/Addis_Ababa",
            "date_format": "d/m/Y",
            "time_format": "24",
        }
    )

    if request.method == "POST":

        settings.system_name = request.POST.get(
            "system_name", ""
        ).strip()

        settings.system_code = request.POST.get(
            "system_code", ""
        ).strip()

        settings.organization = request.POST.get(
            "organization", ""
        ).strip()

        settings.location = request.POST.get(
            "location", ""
        ).strip()

        settings.timezone = request.POST.get(
            "timezone", "Africa/Addis_Ababa"
        ).strip()

        settings.date_format = request.POST.get(
            "date_format", "d/m/Y"
        ).strip()

        settings.time_format = request.POST.get(
            "time_format", "24"
        ).strip()

        settings.save()

        messages.success(
            request,
            "General settings saved successfully."
        )

        return redirect("system_settings:general")

    return render(
        request,
        "system_settings/general.html",
        {"settings": settings}
    )


@login_required
def security_settings(request):

    settings, created = SecuritySetting.objects.get_or_create(
        pk=1,
        defaults={
            "session_timeout_minutes": 30,
            "max_login_attempts": 5,
            "lockout_duration_minutes": 15,
            "password_min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_number": True,
            "require_special_character": True,
            "password_authentication": True,
            "fingerprint_authentication": True,
            "rfid_authentication": True,
            "face_authentication": True,
            "is_active": True,
        }
    )

    if request.method == "POST":

        settings.session_timeout_minutes = int(
            request.POST.get(
                "session_timeout_minutes", 30
            )
        )

        settings.max_login_attempts = int(
            request.POST.get(
                "max_login_attempts", 5
            )
        )

        settings.lockout_duration_minutes = int(
            request.POST.get(
                "lockout_duration_minutes", 15
            )
        )

        settings.password_min_length = int(
            request.POST.get(
                "password_min_length", 8
            )
        )

        settings.require_uppercase = (
            "require_uppercase" in request.POST
        )

        settings.require_lowercase = (
            "require_lowercase" in request.POST
        )

        settings.require_number = (
            "require_number" in request.POST
        )

        settings.require_special_character = (
            "require_special_character" in request.POST
        )

        settings.password_authentication = (
            "password_authentication" in request.POST
        )

        settings.fingerprint_authentication = (
            "fingerprint_authentication" in request.POST
        )

        settings.rfid_authentication = (
            "rfid_authentication" in request.POST
        )

        settings.face_authentication = (
            "face_authentication" in request.POST
        )

        settings.is_active = (
            "is_active" in request.POST
        )

        settings.save()

        messages.success(
            request,
            "Security settings saved successfully."
        )

        return redirect("system_settings:security")

    return render(
        request,
        "system_settings/security.html",
        {"settings": settings}
    )

@login_required
def access_control_settings(request):

    settings, created = AccessControlSetting.objects.get_or_create(
        pk=1,
        defaults={
            "default_access_behavior": "deny",
            "default_unlock_duration_seconds": 5,
            "max_unlock_duration_seconds": 30,
            "auto_lock_enabled": True,
            "log_successful_access": True,
            "log_denied_access": True,
            "log_door_events": True,
            "access_denial_logging": True,
            "access_denied_notifications": True,
            "working_hours_enabled": False,
            "work_start_time": "08:00",
            "work_end_time": "17:00",
            "weekend_access_allowed": False,
            "is_active": True,
        }
    )

    if request.method == "POST":

        settings.default_access_behavior = request.POST.get(
            "default_access_behavior",
            "deny"
        )

        settings.default_unlock_duration_seconds = int(
            request.POST.get(
                "default_unlock_duration_seconds",
                5
            )
        )

        settings.max_unlock_duration_seconds = int(
            request.POST.get(
                "max_unlock_duration_seconds",
                30
            )
        )

        settings.auto_lock_enabled = (
            "auto_lock_enabled" in request.POST
        )

        settings.log_successful_access = (
            "log_successful_access" in request.POST
        )

        settings.log_denied_access = (
            "log_denied_access" in request.POST
        )

        settings.log_door_events = (
            "log_door_events" in request.POST
        )

        settings.access_denial_logging = (
            "access_denial_logging" in request.POST
        )

        settings.access_denied_notifications = (
            "access_denied_notifications" in request.POST
        )

        settings.working_hours_enabled = (
            "working_hours_enabled" in request.POST
        )

        settings.work_start_time = request.POST.get(
            "work_start_time",
            
        ) or "08:00"

        settings.work_end_time = request.POST.get(
            "work_end_time",
           
        ) or "20:00"

        settings.weekend_access_allowed = (
            "weekend_access_allowed" in request.POST
        )

        settings.is_active = (
            "is_active" in request.POST
        )

        settings.save()

        messages.success(
            request,
            "Access control settings saved successfully."
        )

        return redirect(
            "system_settings:access_control"
        )

    return render(
        request,
        "system_settings/access_control.html",
        {"settings": settings}
    )

@login_required
def biometric_settings(request):

    settings, created = BiometricSetting.objects.get_or_create(
        pk=1,
        defaults={
            "fingerprint_enabled": True,
            "fingerprint_match_threshold": 50,
            "fingerprint_timeout": 10,
            "face_enabled": True,
            "face_match_threshold": 70,
            "face_scan_timeout": 10,
            "allow_enrollment": True,
            "require_employee": True,
            "is_active": True,
        }
    )

    if request.method == "POST":

        # ==============================
        # FINGERPRINT SETTINGS
        # ==============================

        settings.fingerprint_enabled = (
            "fingerprint_enabled" in request.POST
        )

        settings.fingerprint_match_threshold = int(
            request.POST.get(
                "fingerprint_match_threshold",
                50
            )
        )

        settings.fingerprint_timeout = int(
            request.POST.get(
                "fingerprint_timeout",
                10
            )
        )

        # ==============================
        # FACE RECOGNITION SETTINGS
        # ==============================

        settings.face_enabled = (
            "face_enabled" in request.POST
        )

        settings.face_match_threshold = int(
            request.POST.get(
                "face_match_threshold",
                70
            )
        )

        settings.face_scan_timeout = int(
            request.POST.get(
                "face_scan_timeout",
                10
            )
        )

        # ==============================
        # ENROLLMENT SETTINGS
        # ==============================

        settings.allow_enrollment = (
            "allow_enrollment" in request.POST
        )

        settings.require_employee = (
            "require_employee" in request.POST
        )

        settings.is_active = (
            "is_active" in request.POST
        )

        settings.save()

        messages.success(
            request,
            "Biometric settings saved successfully."
        )

        return redirect(
            "system_settings:biometric"
        )

    return render(
        request,
        "system_settings/biometric.html",
        {
            "settings": settings
        }
    )

@login_required
def device_settings(request):

    settings, created = DeviceSetting.objects.get_or_create(
        pk=1,
        defaults={
            "devices_enabled": True,
            "connection_timeout": 10,
            "heartbeat_interval": 30,
            "device_monitoring": True,
            "offline_notifications": True,
            "require_registered_device": True,
            "reject_inactive_devices": True,
            "api_enabled": True,
            "api_logging": True,
            "is_active": True,
        }
    )

    if request.method == "POST":

        settings.devices_enabled = (
            "devices_enabled" in request.POST
        )

        settings.connection_timeout = int(
            request.POST.get(
                "connection_timeout",
                10
            )
        )

        settings.heartbeat_interval = int(
            request.POST.get(
                "heartbeat_interval",
                30
            )
        )

        settings.device_monitoring = (
            "device_monitoring" in request.POST
        )

        settings.offline_notifications = (
            "offline_notifications" in request.POST
        )

        settings.require_registered_device = (
            "require_registered_device" in request.POST
        )

        settings.reject_inactive_devices = (
            "reject_inactive_devices" in request.POST
        )

        settings.api_enabled = (
            "api_enabled" in request.POST
        )

        settings.api_logging = (
            "api_logging" in request.POST
        )

        settings.is_active = (
            "is_active" in request.POST
        )

        settings.save()

        messages.success(
            request,
            "Device settings saved successfully."
        )

        return redirect(
            "system_settings:devices"
        )

    return render(
        request,
        "system_settings/devices.html",
        {
            "settings": settings
        }
    )

@login_required
def notification_settings(request):
    return render(
        request,
        "system_settings/notifications.html",
    )

