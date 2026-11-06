from django.urls import path

from . import views


app_name = "devices"


urlpatterns = [

    path(
        "",
        views.device_list,
        name="device_list",
    ),

    path(
        "add/",
        views.device_add,
        name="device_add",
    ),

    # ESP32 API
    path(
        "api/register/",
        views.device_register_api,
        name="device_register_api",
    ),

    path(
        "<int:device_id>/",
        views.device_detail,
        name="device_detail",
    ),

    path(
        "<int:device_id>/edit/",
        views.device_edit,
        name="device_edit",
    ),

    path(
        "<int:device_id>/toggle-status/",
        views.device_toggle_status,
        name="device_toggle_status",
    ),

    path(
        "<int:device_id>/delete/",
        views.device_delete,
        name="device_delete",
    ),
]