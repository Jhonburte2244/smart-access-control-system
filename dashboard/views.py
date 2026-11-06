from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import ExtractHour

from employees.models import Employee
from doors.models import Door
from attendance.models import Attendance
from access_control.models import AccessLog
from devices.models import Device
from incidents.models import Incident
from notifications.models import Notification


@login_required
def dashboard(request):

    today = timezone.localdate()

    # ==========================================================
    # EMPLOYEES
    # ==========================================================

    total_employees = Employee.objects.count()

    active_employees = Employee.objects.filter(
        status__iexact="active"
    ).count()

    inactive_employees = total_employees - active_employees

    # ==========================================================
    # DOORS
    # ==========================================================

    total_doors = Door.objects.count()

    active_doors = Door.objects.filter(
        is_active=True
    ).count()

    inactive_doors = total_doors - active_doors

    # ==========================================================
    # ATTENDANCE
    # ==========================================================

    today_attendance = Attendance.objects.filter(
        attendance_date=today
    )

    present_today = today_attendance.count()

    # Employees with late arrival
    late_today = today_attendance.filter(
        late_minutes__gt=0
    ).count()

    # Employees with early departure
    early_departure_today = today_attendance.filter(
        early_leave_minutes__gt=0
    ).count()
     
     
    # ==========================================================
    # DEVICES
    # ==========================================================
    total_devices = Device.objects.count()
    active_devices = Device.objects.filter(is_active=True).count()
    inactive_devices = Device.objects.filter(is_active=False).count()

    recent_devices = Device.objects.order_by("-last_seen", "device_code")[:5]
    # ==========================================
    # DEVICE ONLINE / OFFLINE STATUS
    # ==========================================

    now = timezone.now()

    for device in recent_devices:

        if not device.last_seen:
            device.connection_status = "offline"

        else:
            seconds_since_seen = (now - device.last_seen).total_seconds()

            if seconds_since_seen <= 120:
                device.connection_status = "online"

            elif seconds_since_seen <= 600:
                device.connection_status = "warning"

            else:
                device.connection_status = "offline"
     
    # ==========================================================
    # ACCESS LOGS - TODAY
    # ==========================================================

    today_logs = AccessLog.objects.filter(
        event_time__date=today
    )

    total_access_today = today_logs.count()

    access_granted = today_logs.filter(
        action__iexact="granted"
    ).count()

    access_denied = today_logs.filter(
        action__iexact="denied"
    ).count()

    # ==========================================================
    # ACCESS SUCCESS RATE
    # ==========================================================

    if total_access_today > 0:
        access_success_rate = round(
            (access_granted / total_access_today) * 100
        )

        access_denied_rate = round(
            (access_denied / total_access_today) * 100
        )
    else:
        access_success_rate = 0
        access_denied_rate = 0

    # ==========================================================
    # AUTHENTICATION METHODS
    # ==========================================================

    fingerprint_count = today_logs.filter(
        authentication_method__icontains="finger"
    ).count()

    rfid_count = today_logs.filter(
        authentication_method__icontains="rfid"
    ).count()

    face_count = today_logs.filter(
        authentication_method__icontains="face"
    ).count()

    # ==========================================================
    # ACCESS ACTIVITY BY HOUR
    # ==========================================================

    hourly_access = (
        today_logs
        .annotate(
            hour=ExtractHour("event_time")
        )
        .values("hour")
        .annotate(
            total=Count("id")
        )
        .order_by("hour")
    )

    # Create all 24 hours so the chart does not have gaps
    hourly_data = [0] * 24

    for item in hourly_access:
        hour = item["hour"]

        if hour is not None:
            hourly_data[int(hour)] = item["total"]

    # ==========================================================
    # GRANTED / DENIED BY HOUR
    # ==========================================================

    hourly_granted_query = (
        today_logs
        .filter(action__iexact="granted")
        .annotate(
            hour=ExtractHour("event_time")
        )
        .values("hour")
        .annotate(
            total=Count("id")
        )
        .order_by("hour")
    )

    hourly_denied_query = (
        today_logs
        .filter(action__iexact="denied")
        .annotate(
            hour=ExtractHour("event_time")
        )
        .values("hour")
        .annotate(
            total=Count("id")
        )
        .order_by("hour")
    )

    hourly_granted = [0] * 24
    hourly_denied = [0] * 24

    for item in hourly_granted_query:
        hour = item["hour"]

        if hour is not None:
            hourly_granted[int(hour)] = item["total"]

    for item in hourly_denied_query:
        hour = item["hour"]

        if hour is not None:
            hourly_denied[int(hour)] = item["total"]

    # ==========================================================
    # RECENT ACCESS ACTIVITY
    # ==========================================================

    recent_logs = (
        AccessLog.objects
        .select_related(
            "employee",
            "door",
            "rfid_card",
        )
        .order_by("-event_time")[:10]
    )

    # ==========================================================
    # DOOR ACTIVITY
    # ==========================================================

    door_activity = []

    for door in Door.objects.all().order_by("id"):

        door_logs_today = today_logs.filter(
            door=door
        )

        door_granted = door_logs_today.filter(
            action__iexact="granted"
        ).count()

        door_denied = door_logs_today.filter(
            action__iexact="denied"
        ).count()

        door_activity.append({
            "door": door,
            "total": door_logs_today.count(),
            "granted": door_granted,
            "denied": door_denied,
        })
    
    # ==========================================================
    # INCIDENT MONITORING
    # ==========================================================

    total_incidents = Incident.objects.count()

    open_incidents = Incident.objects.filter(
        status__iexact="open"
    ).count()

    critical_incidents = Incident.objects.filter(
        severity__iexact="critical"
    ).exclude(
        status__in=["resolved", "closed"]
    ).count()

    resolved_incidents = Incident.objects.filter(
        status__iexact="resolved"
    ).count()

    recent_incidents = (
        Incident.objects
        .select_related("employee", "door")
        .order_by("-reported_at")[:5]
    )

    # ==========================================================
    # NOTIFICATION MONITORING
    # ==========================================================

    total_notifications = Notification.objects.count()

    unread_notifications = Notification.objects.filter(
        is_read=False
    ).count()

    read_notifications = Notification.objects.filter(
        is_read=True
    ).count()

    recent_notifications = (
        Notification.objects
        .select_related("employee")
        .order_by("-created_at")[:5]
    )

    # ==========================================================
    # DASHBOARD CONTEXT
    # ==========================================================

    context = {

        # ------------------------------------------------------
        # General
        # ------------------------------------------------------

        "today": today,

        # ------------------------------------------------------
        # Employees
        # ------------------------------------------------------

        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": inactive_employees,

        # ------------------------------------------------------
        # Doors
        # ------------------------------------------------------

        "total_doors": total_doors,
        "active_doors": active_doors,
        "inactive_doors": inactive_doors,
        "door_activity": door_activity,
        
        # ------------------------------------------------------
        # Device
        # ------------------------------------------------------
        
        "total_devices": total_devices,
        "active_devices": active_devices,
        "inactive_devices": inactive_devices,
        "recent_devices": recent_devices,

        # ------------------------------------------------------
        # Attendance
        # ------------------------------------------------------

        "present_today": present_today,
        "late_today": late_today,
        "early_departure_today": early_departure_today,

        # ------------------------------------------------------
        # Access
        # ------------------------------------------------------

        "total_access_today": total_access_today,
        "access_granted": access_granted,
        "access_denied": access_denied,

        "access_success_rate": access_success_rate,
        "access_denied_rate": access_denied_rate,

        # ------------------------------------------------------
        # Authentication
        # ------------------------------------------------------

        "fingerprint_count": fingerprint_count,
        "rfid_count": rfid_count,
        "face_count": face_count,

        # ------------------------------------------------------
        # Charts
        # ------------------------------------------------------

        "hourly_data": hourly_data,
        "hourly_granted": hourly_granted,
        "hourly_denied": hourly_denied,

        # ------------------------------------------------------
        # Recent activity
        # ------------------------------------------------------

        "recent_logs": recent_logs,
        
        # ------------------------------------------------------
        # Incidents
        # ------------------------------------------------------

        "total_incidents": total_incidents,
        "open_incidents": open_incidents,
        "critical_incidents": critical_incidents,
        "resolved_incidents": resolved_incidents,
        "recent_incidents": recent_incidents,

        # ------------------------------------------------------
        # Notifications
        # ------------------------------------------------------

        "total_notifications": total_notifications,
        "unread_notifications": unread_notifications,
        "read_notifications": read_notifications,
        "recent_notifications": recent_notifications,

    }

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )