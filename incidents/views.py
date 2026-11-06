
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from notifications.models import Notification
from .models import Incident
from django.views.decorators.http import require_POST

def create_incident_notification(incident, action):
    """Create a notification for an incident action."""

    notification_types = {
        "low": "info",
        "medium": "warning",
        "high": "danger",
        "critical": "security",
    }

    Notification.objects.create(
        user=None,
        employee_id=incident.employee_id,
        title=f"Incident {action}: #{incident.pk}",
        message=(
            f"Incident ID: {incident.pk}\n"
            f"Type: {incident.incident_type}\n"
            f"Severity: {incident.severity.title()}\n"
            f"New status: {incident.status.title()}\n"
            f"Action: {action}."
        ),
        notification_type=notification_types.get(
            incident.severity,
            "info",
        ),
        is_read=False,
        created_at=timezone.now(),
    )


@login_required
def incident_list(request):
    # Base queryset for the incident table
    incidents = Incident.objects.select_related(
        "employee",
        "door",
    ).all()

    # Read filter values
    search = request.GET.get("search", "").strip()
    severity = request.GET.get("severity", "").strip()
    status = request.GET.get("status", "").strip()

    # Search incidents, employees, and doors
    if search:
        incidents = incidents.filter(
            Q(incident_type__icontains=search)
            | Q(description__icontains=search)
            | Q(employee__first_name__icontains=search)
            | Q(employee__last_name__icontains=search)
            | Q(employee__employee_number__icontains=search)
            | Q(door__name__icontains=search)
        )

    # Apply valid severity filter
    if severity in dict(Incident.SEVERITY_CHOICES):
        incidents = incidents.filter(severity=severity)

    # Apply valid status filter
    if status in dict(Incident.STATUS_CHOICES):
        incidents = incidents.filter(status=status)

    # Show the newest incidents first
    incidents = incidents.order_by("-reported_at")

    # Summary counts remain independent of table filters
    context = {
        "incidents": incidents,
        "search": search,
        "selected_severity": severity,
        "selected_status": status,
        "severity_choices": Incident.SEVERITY_CHOICES,
        "status_choices": Incident.STATUS_CHOICES,

        "total_incidents": Incident.objects.count(),
        "open_incidents": Incident.objects.filter(
            status="open"
        ).count(),
        "investigating_incidents": Incident.objects.filter(
            status="investigating"
        ).count(),
        "resolved_incidents": Incident.objects.filter(
            status="resolved"
        ).count(),
        "closed_incidents": Incident.objects.filter(
            status="closed"
        ).count(),
    }

    return render(
        request,
        "incidents/list.html",
        context,
    )


@login_required
def incident_detail(request, pk):
    incident = get_object_or_404(
        Incident.objects.select_related("employee", "door"),
        pk=pk,
    )

    return render(
        request,
        "incidents/detail.html",
        {"incident": incident},
    )


@login_required
def incident_create(request):
    from employees.models import Employee
    from doors.models import Door

    if request.method == "POST":
        incident_type = request.POST.get(
            "incident_type", ""
        ).strip()
        severity = request.POST.get("severity", "medium")
        description = request.POST.get("description", "").strip()

        if not incident_type:
            messages.error(request, "Incident type is required.")
            return redirect("incidents:incident_create")

        if severity not in dict(Incident.SEVERITY_CHOICES):
            messages.error(request, "Invalid incident severity.")
            return redirect("incidents:incident_create")

        now = timezone.now()

        # All new incidents must start as Open.
        incident = Incident(
            incident_type=incident_type,
            severity=severity,
            status="open",
            description=description or None,
            reported_at=now,
            created_at=now,
        )

        employee_id = request.POST.get("employee_id") or None
        door_id = request.POST.get("door_id") or None

        if employee_id:
            incident.employee_id = employee_id

        if door_id:
            incident.door_id = door_id

        incident.save(force_insert=True)

        create_incident_notification(incident, "Reported")

        messages.success(
            request,
            "Incident created successfully and notification generated.",
        )

        return redirect("incidents:incident_list")

    context = {
        "employees": Employee.objects.all().order_by(
            "employee_number"
        ),
        "doors": Door.objects.filter(
            is_active=True
        ).order_by("name"),
        "severity_choices": Incident.SEVERITY_CHOICES,
        "status_choices": Incident.STATUS_CHOICES,
    }

    return render(request, "incidents/form.html", context)


@login_required
def incident_edit(request, pk):
    from employees.models import Employee
    from doors.models import Door

    incident = get_object_or_404(
        Incident.objects.select_related("employee", "door"),
        pk=pk,
    )

    if request.method == "POST":
        if incident.status == "closed":
            messages.error(
                request,
                "Closed incidents cannot be edited.",
            )
            return redirect(
                "incidents:incident_detail",
                pk=incident.pk,
            )

        incident_type = request.POST.get(
            "incident_type", ""
        ).strip()
        severity = request.POST.get(
            "severity", incident.severity
        )
        new_status = request.POST.get(
            "status", incident.status
        )
        description = request.POST.get(
            "description", ""
        ).strip()

        valid_severities = dict(Incident.SEVERITY_CHOICES)
        valid_statuses = dict(Incident.STATUS_CHOICES)

        if not incident_type:
            messages.error(
                request,
                "Incident type is required.",
            )
            return redirect(
                "incidents:incident_edit",
                pk=incident.pk,
            )

        if severity not in valid_severities:
            messages.error(
                request,
                "Invalid incident severity.",
            )
            return redirect(
                "incidents:incident_edit",
                pk=incident.pk,
            )

        if new_status not in valid_statuses:
            messages.error(
                request,
                "Invalid incident status.",
            )
            return redirect(
                "incidents:incident_edit",
                pk=incident.pk,
            )

        # Enforce the incident lifecycle.
        allowed_transitions = {
            "open": {"open", "investigating"},
            "investigating": {"investigating", "resolved"},
            "resolved": {"resolved", "closed"},
        }

        if new_status not in allowed_transitions.get(
            incident.status, set()
        ):
            messages.error(
                request,
                f"Invalid status transition from "
                f"{incident.get_status_display()} to "
                f"{valid_statuses[new_status]}.",
            )
            return redirect(
                "incidents:incident_edit",
                pk=incident.pk,
            )

        old_status = incident.status
        old_severity = incident.severity

        employee_id = request.POST.get("employee_id") or None
        door_id = request.POST.get("door_id") or None

        incident.incident_type = incident_type
        incident.severity = severity
        incident.status = new_status
        incident.description = description or None
        incident.employee_id = employee_id
        incident.door_id = door_id

        if new_status in {"resolved", "closed"}:
            if not incident.resolved_at:
                incident.resolved_at = timezone.now()
        else:
            incident.resolved_at = None
            incident.resolved_by = None

        incident.save()

        if old_status != new_status:
            create_incident_notification(
                incident,
                "Status Updated",
            )
            messages.success(
                request,
                f"Incident status changed to "
                f"{incident.get_status_display()}.",
            )
        elif old_severity != severity:
            create_incident_notification(
                incident,
                "Severity Updated",
            )
            messages.success(
                request,
                "Incident severity updated and notification generated.",
            )
        else:
            messages.success(
                request,
                "Incident updated successfully.",
            )

        return redirect(
            "incidents:incident_detail",
            pk=incident.pk,
        )

    context = {
        "incident": incident,
        "employees": Employee.objects.all().order_by(
            "employee_number"
        ),
        "doors": Door.objects.filter(
            is_active=True
        ).order_by("name"),
        "severity_choices": Incident.SEVERITY_CHOICES,
        "status_choices": Incident.STATUS_CHOICES,
        "edit_mode": True,
    }

    return render(request, "incidents/form.html", context)


def _transition_incident(
    request,
    pk,
    required_status,
    new_status,
    notification_title,
    warning_message,
    success_message,
    set_resolved=False,
):
    incident = get_object_or_404(Incident, pk=pk)

    if incident.status != required_status:
        messages.warning(request, warning_message)
    else:
        incident.status = new_status
        update_fields = ["status"]

        if set_resolved:
            incident.resolved_at = timezone.now()
            update_fields.append("resolved_at")

        incident.save(update_fields=update_fields)

        create_incident_notification(
            incident,
            notification_title,
        )

        messages.success(request, success_message)

    return redirect(
        "incidents:incident_detail",
        pk=incident.pk,
    )


@login_required
@require_POST
def incident_investigate(request, pk):
    return _transition_incident(
        request=request,
        pk=pk,
        required_status="open",
        new_status="investigating",
        notification_title="Investigation Started",
        warning_message="Only open incidents can move to Investigating.",
        success_message=(
            "Incident moved to Investigating. Notification generated."
        ),
    )


@login_required
@require_POST
def incident_resolve(request, pk):
    return _transition_incident(
        request=request,
        pk=pk,
        required_status="investigating",
        new_status="resolved",
        notification_title="Resolved",
        warning_message=(
            "Only incidents under investigation can be resolved."
        ),
        success_message=(
            "Incident resolved and notification generated."
        ),
        set_resolved=True,
    )


@login_required
@require_POST
def incident_close(request, pk):
    return _transition_incident(
        request=request,
        pk=pk,
        required_status="resolved",
        new_status="closed",
        notification_title="Closed",
        warning_message="Only resolved incidents can be closed.",
        success_message=(
            "Incident closed and notification generated."
        ),
    )
