
from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.notification_list, name="notification_list"),

    # Bulk action
    path(
        "mark-all-read/",
        views.notification_mark_all_read,
        name="notification_mark_all_read",
    ),

    # Individual notification actions
    path(
        "<int:pk>/read/",
        views.notification_mark_read,
        name="notification_mark_read",
    ),
    path(
        "<int:pk>/unread/",
        views.notification_mark_unread,
        name="notification_mark_unread",
    ),
    path(
        "<int:pk>/",
        views.notification_detail,
        name="notification_detail",
    ),
]
