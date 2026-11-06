from django.db import models


class SystemSetting(models.Model):
    system_name = models.CharField(
        max_length=200,
        default="Smart Access Control System",
    )

    system_code = models.CharField(
        max_length=50,
        default="SMAC",
    )

    organization = models.CharField(
        max_length=200,
        blank=True,
    )

    location = models.CharField(
        max_length=200,
        blank=True,
    )

    timezone = models.CharField(
        max_length=100,
        default="Africa/Addis_Ababa",
    )

    date_format = models.CharField(
        max_length=50,
        default="d/m/Y",
    )

    time_format = models.CharField(
        max_length=50,
        default="24",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "system_settings"

    def __str__(self):
        return self.system_name
        
        
class SecuritySetting(models.Model):
    """
    Stores security-related configuration for the Smart Access Control System.
    """

    session_timeout_minutes = models.PositiveIntegerField(
        default=30,
        verbose_name="Session Timeout (minutes)"
    )

    max_login_attempts = models.PositiveIntegerField(
        default=5,
        verbose_name="Maximum Login Attempts"
    )

    lockout_duration_minutes = models.PositiveIntegerField(
        default=15,
        verbose_name="Account Lockout Duration (minutes)"
    )

    password_min_length = models.PositiveIntegerField(
        default=8,
        verbose_name="Minimum Password Length"
    )

    require_uppercase = models.BooleanField(
        default=True
    )

    require_lowercase = models.BooleanField(
        default=True
    )

    require_number = models.BooleanField(
        default=True
    )

    require_special_character = models.BooleanField(
        default=True
    )

    password_authentication = models.BooleanField(
        default=True
    )

    fingerprint_authentication = models.BooleanField(
        default=True
    )

    rfid_authentication = models.BooleanField(
        default=True
    )

    face_authentication = models.BooleanField(
        default=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "security_settings"
        verbose_name = "Security Setting"
        verbose_name_plural = "Security Settings"

    def __str__(self):
        return "Security Settings"
        
class AccessControlSetting(models.Model):
    """
    Stores access-control configuration for the Smart Access Control System.
    """

    default_access_behavior = models.CharField(
        max_length=20,
        choices=[
            ("allow", "Allow Access"),
            ("deny", "Deny Access"),
        ],
        default="deny",
    )

    default_unlock_duration_seconds = models.PositiveIntegerField(
        default=5,
        verbose_name="Default Door Unlock Duration (seconds)"
    )

    max_unlock_duration_seconds = models.PositiveIntegerField(
        default=30,
        verbose_name="Maximum Door Unlock Duration (seconds)"
    )

    auto_lock_enabled = models.BooleanField(
        default=True,
        verbose_name="Automatic Door Lock"
    )

    log_successful_access = models.BooleanField(
        default=True,
        verbose_name="Log Successful Access"
    )

    log_denied_access = models.BooleanField(
        default=True,
        verbose_name="Log Denied Access"
    )

    log_door_events = models.BooleanField(
        default=True,
        verbose_name="Log Door Events"
    )

    access_denial_logging = models.BooleanField(
        default=True,
        verbose_name="Access Denial Logging"
    )

    access_denied_notifications = models.BooleanField(
        default=True,
        verbose_name="Access Denied Notifications"
    )

    working_hours_enabled = models.BooleanField(
        default=False,
        verbose_name="Enable Working Hours"
    )

    work_start_time = models.TimeField(
        default="08:00",
        verbose_name="Working Hours Start"
    )

    work_end_time = models.TimeField(
        default="17:00",
        verbose_name="Working Hours End"
    )

    weekend_access_allowed = models.BooleanField(
        default=False,
        verbose_name="Allow Weekend Access"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Access Control Settings Active"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "access_control_settings"
        verbose_name = "Access Control Setting"
        verbose_name_plural = "Access Control Settings"

    def __str__(self):
        return "Access Control Settings"
      

class BiometricSetting(models.Model):
    """
    Stores biometric authentication configuration
    for the Smart Access Control System.
    """

    fingerprint_enabled = models.BooleanField(
        default=True,
        verbose_name="Enable Fingerprint Authentication"
    )

    fingerprint_match_threshold = models.PositiveIntegerField(
        default=50,
        verbose_name="Fingerprint Match Threshold"
    )

    fingerprint_timeout = models.PositiveIntegerField(
        default=10,
        verbose_name="Fingerprint Scan Timeout (seconds)"
    )

    face_enabled = models.BooleanField(
        default=True,
        verbose_name="Enable Face Recognition"
    )

    face_match_threshold = models.PositiveIntegerField(
        default=70,
        verbose_name="Face Match Threshold"
    )

    face_scan_timeout = models.PositiveIntegerField(
        default=10,
        verbose_name="Face Scan Timeout (seconds)"
    )

    allow_enrollment = models.BooleanField(
        default=True,
        verbose_name="Allow Biometric Enrollment"
    )

    require_employee = models.BooleanField(
        default=True,
        verbose_name="Require Employee Association"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Biometric Settings Active"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "biometric_settings"
        verbose_name = "Biometric Setting"
        verbose_name_plural = "Biometric Settings"

    def __str__(self):
        return "Biometric Settings"
        
class DeviceSetting(models.Model):
    """
    Stores global device configuration for the
    Smart Access Control System.
    """

    # ==============================
    # DEVICE SYSTEM
    # ==============================

    devices_enabled = models.BooleanField(
        default=True,
        verbose_name="Enable Device System"
    )

    # ==============================
    # DEVICE COMMUNICATION
    # ==============================

    connection_timeout = models.PositiveIntegerField(
        default=10,
        verbose_name="Connection Timeout (seconds)"
    )

    heartbeat_interval = models.PositiveIntegerField(
        default=30,
        verbose_name="Heartbeat Interval (seconds)"
    )

    # ==============================
    # DEVICE MONITORING
    # ==============================

    device_monitoring = models.BooleanField(
        default=True,
        verbose_name="Enable Device Monitoring"
    )

    offline_notifications = models.BooleanField(
        default=True,
        verbose_name="Notify When Device Goes Offline"
    )

    # ==============================
    # DEVICE SECURITY
    # ==============================

    require_registered_device = models.BooleanField(
        default=True,
        verbose_name="Require Registered Device"
    )

    reject_inactive_devices = models.BooleanField(
        default=True,
        verbose_name="Reject Inactive Devices"
    )

    # ==============================
    # HARDWARE API
    # ==============================

    api_enabled = models.BooleanField(
        default=True,
        verbose_name="Enable Hardware API"
    )

    api_logging = models.BooleanField(
        default=True,
        verbose_name="Enable API Logging"
    )

    # ==============================
    # STATUS
    # ==============================

    is_active = models.BooleanField(
        default=True,
        verbose_name="Device Settings Active"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "device_settings"
        verbose_name = "Device Setting"
        verbose_name_plural = "Device Settings"

    def __str__(self):
        return "Device Settings"
        
        
    class Meta:
        db_table = "device_settings"
        verbose_name = "Device Setting"
        verbose_name_plural = "Device Settings"

    def __str__(self):
        return "Device Settings"