
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Notification
from incidents.models import Incident

@login_required
def notification_list(request):
    # Counts across all notifications, before applying filters.
    total_count = Notification.objects.count()
    unread_count = Notification.objects.filter(is_read=False).count()
    read_count = Notification.objects.filter(is_read=True).count()

    notifications = Notification.objects.select_related(
        "employee"
    ).all()

    search_query = request.GET.get("q", "").strip()
    filter_type = request.GET.get("type", "").strip()
    status = request.GET.get("status", "").strip()

    if search_query:
        notifications = notifications.filter(
            Q(title__icontains=search_query)
            | Q(message__icontains=search_query)
        )

    valid_types = {
        value for value, label
        in Notification.NOTIFICATION_TYPE_CHOICES
    }

    if filter_type in valid_types:
        notifications = notifications.filter(
            notification_type=filter_type
        )

    if status == "unread":
        notifications = notifications.filter(is_read=False)
    elif status == "read":
        notifications = notifications.filter(is_read=True)

    context = {
        "notifications": notifications,
        "search_query": search_query,
        "filter_type": filter_type,
        "status": status,
        "notification_types": Notification.NOTIFICATION_TYPE_CHOICES,
        "total_count": total_count,
        "unread_count": unread_count,
        "read_count": read_count,
    }

    return render(request, "notifications/list.html", context)

@login_required
def notification_detail(request, pk):
    notification = get_object_or_404(
        Notification.objects.select_related("employee"),
        pk=pk,
    )

    # Mark notification as read when opened.
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=["is_read", "read_at"])

    # Find the related incident using the ID in the message.
    incident = None
    incident_id = None

    if notification.title.startswith("Incident "):
        for line in notification.message.splitlines():
            if line.startswith("Incident ID:"):
                try:
                    incident_id = int(
                        line.split(":", 1)[1].strip()
                    )
                except (ValueError, IndexError):
                    incident_id = None
                break

        if incident_id is not None:
            incident = Incident.objects.filter(
                pk=incident_id
            ).first()

    context = {
        "notification": notification,
        "incident": incident,
    }

    return render(
        request,
        "notifications/detail.html",
        context,
    )


@login_required
@require_POST
def notification_mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk)

    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=["is_read", "read_at"])
        messages.success(request, "Notification marked as read.")
    else:
        messages.info(request, "This notification is already read.")

    return redirect("notifications:notification_list")


@login_required
@require_POST
def notification_mark_unread(request, pk):
    notification = get_object_or_404(Notification, pk=pk)

    if notification.is_read:
        notification.is_read = False
        notification.read_at = None
        notification.save(update_fields=["is_read", "read_at"])
        messages.success(request, "Notification marked as unread.")
    else:
        messages.info(request, "This notification is already unread.")

    return redirect("notifications:notification_list")


@login_required
@require_POST
def notification_mark_all_read(request):
    updated_count = Notification.objects.filter(
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now(),
    )

    messages.success(
        request,
        f"{updated_count} notification(s) marked as read.",
    )

    return redirect("notifications:notification_list")
