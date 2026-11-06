from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    # Dashboard
    path("", include("dashboard.urls")),

    # Admin
    path("admin/", admin.site.urls),

    # Accounts
    path("accounts/", include("accounts.urls")),

    # Employees
    path("employees/", include("employees.urls")),

    # Departments
    path("departments/", include("departments.urls")),

    # Access Control
    path("access-control/", include("access_control.urls")),

    # Attendance
    path("attendance/", include("attendance.urls")),

    # Access Logs
    path("logs/", include("logs.urls")),

    # RFID Cards
    path("rfid-cards/", include("rfid_cards.urls")),

    # Fingerprints
    path("fingerprints/", include("fingerprints.urls")),
    
    #devices
    path("devices/", include("devices.urls")),
    
    #incidents
    path("incidents/", include("incidents.urls")),
    
    #Notifications
    path("notifications/", include("notifications.urls")),
    
    # System Setting
    path("settings/", include("system_settings.urls")),
    
    path("face-recognition/", include("face_recognition.urls")),
    
]