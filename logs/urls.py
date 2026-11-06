from django.urls import path

from . import views
from access_control import views as access_views

app_name = "logs"

urlpatterns = [
    # Unified Access Logs page
    path(
        "",
        views.access_logs,
        name="access_logs",
    ),

    # View an individual access log
    path(
        "detail/<int:log_id>/",
        access_views.access_log_detail,
        name="access_log_detail",
    ),

    # Export filtered access logs
    path(
        "export/csv/",
        access_views.export_access_logs_csv,
        name="export_access_logs_csv",
    ),

    path(
        "export/pdf/",
        access_views.export_access_logs_pdf,
        name="export_access_logs_pdf",
    ),

    # Security audit report
    path(
        "security-audit/",
        access_views.security_audit_report,
        name="security_audit_report",
    ),
]