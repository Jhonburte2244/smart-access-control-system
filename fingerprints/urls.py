from django.urls import path

from . import views


app_name = "fingerprints"


urlpatterns = [
    # Fingerprint management
    path(
        "",
        views.fingerprint_list,
        name="fingerprint_list",
    ),

    path(
        "add/",
        views.fingerprint_add,
        name="fingerprint_add",
    ),

    path(
        "<int:fingerprint_id>/",
        views.fingerprint_detail,
        name="fingerprint_detail",
    ),

    path(
        "<int:fingerprint_id>/edit/",
        views.fingerprint_edit,
        name="fingerprint_edit",
    ),

    path(
        "<int:fingerprint_id>/toggle-status/",
        views.fingerprint_toggle_status,
        name="fingerprint_toggle_status",
    ),

    path(
        "<int:fingerprint_id>/delete/",
        views.fingerprint_delete,
        name="fingerprint_delete",
    ),

    # Device/API enrollment
    path(
        "api/enroll/",
        views.fingerprint_enroll_api,
        name="fingerprint_enroll_api",
    ),
]