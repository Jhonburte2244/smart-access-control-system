from django.urls import path

from . import views


app_name = "doors"


urlpatterns = [
    path(
        "",
        views.door_list,
        name="doors",
    ),

    path(
        "<int:door_id>/",
        views.door_detail,
        name="door_detail",
    ),

    path(
        "add/",
        views.door_create,
        name="door_create",
    ),

    path(
        "<int:door_id>/edit/",
        views.door_update,
        name="door_update",
    ),

    path(
        "<int:door_id>/toggle/",
        views.door_toggle_status,
        name="door_toggle_status",
    ),
]