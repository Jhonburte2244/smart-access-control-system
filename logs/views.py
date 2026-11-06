
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from access_control.models import AccessLog
from doors.models import Door


@login_required
def access_logs(request):
    logs = (
        AccessLog.objects
        .select_related(
            "employee",
            "door",
            "rfid_card",
        )
        .order_by("-event_time")
    )

    # ==============================
    # SEARCH
    # ==============================
    search = request.GET.get("search", "").strip()

    if search:
        logs = logs.filter(
            Q(employee__first_name__icontains=search)
            | Q(employee__middle_name__icontains=search)
            | Q(employee__last_name__icontains=search)
            | Q(employee__employee_number__icontains=search)
            | Q(door__name__icontains=search)
            | Q(door__door_code__icontains=search)
        )

    # ==============================
    # DOOR FILTER
    # ==============================
    door_id = request.GET.get("door", "").strip()

    if door_id:
        logs = logs.filter(
            door_id=door_id
        )

    # ==============================
    # AUTHENTICATION METHOD
    # ==============================
    authentication_method = request.GET.get(
        "authentication_method",
        ""
    ).strip()

    if authentication_method:
        logs = logs.filter(
            authentication_method__iexact=authentication_method
        )

    # ==============================
    # ACTION / RESULT
    # ==============================
    action = request.GET.get(
        "action",
        ""
    ).strip()

    if action:
        logs = logs.filter(
            action__iexact=action
        )

    # ==============================
    # DATE FILTER
    # ==============================
    date_from = request.GET.get(
        "date_from",
        ""
    ).strip()

    date_to = request.GET.get(
        "date_to",
        ""
    ).strip()

    if date_from:
        logs = logs.filter(
            event_time__date__gte=date_from
        )

    if date_to:
        logs = logs.filter(
            event_time__date__lte=date_to
        )
    
    
    # ==============================
    # ACCESS MONITORING SUMMARY
    # Overall totals, independent of table filters
    # ==============================
    all_events = AccessLog.objects.all()

    total_events = all_events.count()

    granted_events = all_events.filter(
        Q(action__iexact="granted")
        | Q(action__iexact="grant")
        | Q(action__iexact="allow")
        | Q(action__iexact="allowed")
        | Q(action__iexact="success")
        | Q(action__iexact="successful")
    ).count()

    denied_events = all_events.filter(
        Q(action__iexact="denied")
        | Q(action__iexact="deny")
        | Q(action__iexact="rejected")
        | Q(action__iexact="failed")
        | Q(action__iexact="failure")
    ).count()

    today_events = all_events.filter(
        event_time__date=timezone.localdate()
    ).count()


    # ==============================
    # PAGINATION
    # ==============================
    paginator = Paginator(
        logs,
        20
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    # ==============================
    # FILTER OPTIONS
    # ==============================
    doors = Door.objects.order_by(
        "name"
    )

    authentication_methods = (
        AccessLog.objects
        .exclude(
            authentication_method__isnull=True
        )
        .exclude(
            authentication_method__exact=""
        )
        .values_list(
            "authentication_method",
            flat=True
        )
        .distinct()
        .order_by(
            "authentication_method"
        )
    )

    actions = (
        AccessLog.objects
        .exclude(
            action__isnull=True
        )
        .exclude(
            action__exact=""
        )
        .values_list(
            "action",
            flat=True
        )
        .distinct()
        .order_by(
            "action"
        )
    )

    # ==============================
    # CONTEXT
    # ==============================
    context = {
        "page_obj": page_obj,
        "logs": page_obj.object_list,

        "doors": doors,
        "authentication_methods": authentication_methods,
        "actions": actions,

        "search": search,
        "selected_door": door_id,
        "selected_authentication_method": authentication_method,
        "selected_action": action,

        "date_from": date_from,
        "date_to": date_to,
        "total_events": total_events,
        "granted_events": granted_events,
        "denied_events": denied_events,
        "today_events": today_events,
    }

    return render(
        request,
        "logs/access_logs.html",
        context
    )

