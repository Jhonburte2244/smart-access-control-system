from django.urls import path

from . import views


app_name = "departments"


urlpatterns = [
    path("", views.department_list, name="department_list"),

    path("add/", views.department_add, name="department_add"),

    path(
        "<int:department_id>/",
        views.department_detail,
        name="department_detail",
    ),

    path(
        "<int:department_id>/edit/",
        views.department_edit,
        name="department_edit",
    ),

    path(
        "<int:department_id>/toggle-status/",
        views.department_toggle_status,
        name="department_toggle_status",
    ),

    path(
        "<int:department_id>/delete/",
        views.department_delete,
        name="department_delete",
    ),
]