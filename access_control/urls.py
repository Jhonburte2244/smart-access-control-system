from django.urls import path

from . import views


app_name = "access_control"


urlpatterns = [

    # ============================================================
    # DOORS
    # ============================================================

    # Door List
    path(
        "doors/",
        views.doors,
        name="doors",
    ),

    # Add Door
    path(
        "doors/add/",
        views.door_add,
        name="door_add",
    ),

    # Door Details
    path(
        "doors/<int:door_id>/",
        views.door_detail,
        name="door_detail",
    ),

    # Edit Door
    path(
        "doors/<int:door_id>/edit/",
        views.door_edit,
        name="door_edit",
    ),

    # Activate / Deactivate Door
    path(
        "doors/<int:door_id>/toggle-status/",
        views.door_toggle_status,
        name="door_toggle_status",
    ),

    # Delete Door
    path(
        "doors/<int:door_id>/delete/",
        views.door_delete,
        name="door_delete",
    ),


    # ============================================================
    # ACCESS RULES
    # ============================================================

    path(
        "access-rules/",
        views.access_rule_list,
        name="access_rules",
    ),

    path(
        "access-rules/add/",
        views.access_rule_add,
        name="access_rule_add",
    ),

    path(
        "access-rules/<int:rule_id>/edit/",
        views.access_rule_edit,
        name="access_rule_edit",
    ),

    path(
        "access-rules/<int:rule_id>/toggle-status/",
        views.access_rule_toggle_status,
        name="access_rule_toggle_status",
    ),

    path(
        "access-rules/<int:rule_id>/delete/",
        views.access_rule_delete,
        name="access_rule_delete",
    ),
    path(
       "access-logs/",
        views.access_log_list,
        name="access_logs",
    ),
    
    path(
         "access-logs/<int:log_id>/",
         views.access_log_detail,
         name="access_log_detail",
     ),
     

    path(
         "access-logs/export/csv/",
          views.export_access_logs_csv,
          name="export_access_logs_csv",
    ),

    path(
        "access-logs/export/pdf/",
        views.export_access_logs_pdf,
        name="export_access_logs_pdf",
    ),
    path(
        "security-audit/",
        views.security_audit_report,
        name="security_audit_report",
    ),

  
    # ============================================================
    # PERMISSIONS
    # ============================================================

    path(
        "permissions/",
        views.permission_list,
        name="permissions",
    ),

    path(
        "permissions/add/",
        views.permission_add,
        name="permission_add",
    ),

    path(
        "permissions/<int:permission_id>/edit/",
        views.permission_edit,
        name="permission_edit",
    ),

    path(
        "permissions/<int:permission_id>/toggle-status/",
        views.permission_toggle_status,
        name="permission_toggle_status",
    ),

    path(
        "permissions/<int:permission_id>/delete/",
        views.permission_delete,
        name="permission_delete",
    ),
        # ============================================================
    # ROLES
    # ============================================================

    path(
        "roles/",
        views.role_list,
        name="roles",
    ),

    path(
        "roles/add/",
        views.role_add,
        name="role_add",
    ),

    path(
        "roles/<int:role_id>/",
        views.role_detail,
        name="role_detail",
    ),

    path(
        "roles/<int:role_id>/edit/",
        views.role_edit,
        name="role_edit",
    ),

    path(
        "roles/<int:role_id>/toggle-status/",
        views.role_toggle_status,
        name="role_toggle_status",
    ),

    path(
        "roles/<int:role_id>/delete/",
        views.role_delete,
        name="role_delete",
    ),
    
    path(
        "api/fingerprint-auth/",
        views.fingerprint_authenticate,
        name="fingerprint_authenticate",
    ),
    
    path( 
        "api/access/fingerprint/", 
        views.fingerprint_authenticate, 
        name="fingerprint_authenticate", 
    ),
]

