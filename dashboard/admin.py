from django.contrib import admin

from .models import (
    AccessLogs, AccessRules, Attendance, AttendanceSchedules,
    AuditLogs, Departments, Devices, DoorPermissions, Doors,
    Employees, FaceTemplates, Fingerprints, Incidents,
    Notifications, Permissions, RfidCards, Roles, Shifts, Users,
)

# These models map to existing PostgreSQL tables (managed=False).
# They can be registered for read-only inspection in Django Admin.

for model in [
    AccessLogs, AccessRules, Attendance, AttendanceSchedules,
    AuditLogs, Departments, Devices, DoorPermissions, Doors,
    Employees, FaceTemplates, Fingerprints, Incidents,
    Notifications, Permissions, RfidCards, Roles, Shifts, Users,
]:
    admin.site.register(model)
