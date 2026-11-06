from django.urls import path

from . import views


app_name = "employees"


urlpatterns = [
    path(
        "",
        views.employees,
        name="employees",
    ),

    path(
        "add/",
        views.employee_add,
        name="employee_add",
    ),

    path(
        "<int:employee_id>/",
        views.employee_detail,
        name="employee_detail",
    ),

    path(
        "<int:employee_id>/edit/",
        views.employee_edit,
        name="employee_edit",
    ),

    path(
        "<int:employee_id>/delete/",
        views.employee_delete,
        name="employee_delete",
    ),
]