from django.urls import path
from . import views

app_name = "attendance"

urlpatterns = [
    path(
        "",
        views.attendance_list,
        name="attendance_list",
    ),

    path(
        "weekly/",
        views.attendance_weekly,
        name="attendance_weekly",
    ),

    path(
        "monthly/",
        views.attendance_monthly,
        name="attendance_monthly",
    ),

    path(
        "departments/",
        views.attendance_departments,
        name="attendance_departments",
    ),

    path(
        "reports/",
        views.attendance_reports,
        name="attendance_reports",
    ),

    path(
        "reports/excel/",
        views.attendance_report_excel,
        name="attendance_report_excel",
    ),

    path(
        "reports/pdf/",
        views.attendance_report_pdf,
        name="attendance_report_pdf",
    ),
]