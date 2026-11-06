
from .models import Notification


def notification_counts(request):
    if not request.user.is_authenticated:
        return {
            "sidebar_unread_notifications": 0,
        }

    return {
        "sidebar_unread_notifications": (
            Notification.objects.filter(is_read=False).count()
        ),
    }
