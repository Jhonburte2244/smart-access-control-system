from django.db import models


class AccessLogs(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey("Employees", models.DO_NOTHING, blank=True, null=True)
    door = models.ForeignKey("Doors", models.DO_NOTHING, blank=True, null=True)
    device = models.ForeignKey("Devices", models.DO_NOTHING, blank=True, null=True)
    rfid_card = models.ForeignKey("RfidCards", models.DO_NOTHING, blank=True, null=True)
    authentication_method = models.CharField(max_length=50)
    action = models.CharField(max_length=30)
    reason = models.TextField(blank=True, null=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    event_time = models.DateTimeField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "access_logs"


class AccessRules(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=150)
    description = models.TextField(blank=True, null=True)
    access_type = models.CharField(max_length=30)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    valid_from = models.DateField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()
    saturday = models.BooleanField()
    sunday = models.BooleanField()
    priority = models.IntegerField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "access_rules"


class Attendance(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey("Employees", models.DO_NOTHING)
    shift = models.ForeignKey("Shifts", models.DO_NOTHING, blank=True, null=True)
    attendance_date = models.DateField()
    check_in = models.DateTimeField(blank=True, null=True)
    check_out = models.DateTimeField(blank=True, null=True)
    late_minutes = models.IntegerField()
    early_leave_minutes = models.IntegerField()
    worked_minutes = models.IntegerField()
    overtime_minutes = models.IntegerField()
    status = models.CharField(max_length=30)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "attendance"
        unique_together = (("employee", "attendance_date"),)


class AttendanceSchedules(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey("Employees", models.DO_NOTHING)
    shift = models.ForeignKey("Shifts", models.DO_NOTHING)
    schedule_date = models.DateField(blank=True, null=True)
    day_of_week = models.IntegerField(blank=True, null=True)
    is_working_day = models.BooleanField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "attendance_schedules"


class AuditLogs(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey("Users", models.DO_NOTHING, blank=True, null=True)
    action = models.CharField(max_length=100)
    table_name = models.CharField(max_length=100, blank=True, null=True)
    record_id = models.BigIntegerField(blank=True, null=True)
    old_values = models.JSONField(blank=True, null=True)
    new_values = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "audit_logs"


class Departments(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    manager_name = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "departments"


class Devices(models.Model):
    id = models.BigAutoField(primary_key=True)
    device_code = models.CharField(unique=True, max_length=100)
    device_name = models.CharField(max_length=150)
    device_type = models.CharField(max_length=50)
    serial_number = models.CharField(unique=True, max_length=150, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    mac_address = models.CharField(max_length=50, blank=True, null=True)
    firmware_version = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=30)
    last_seen = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "devices"


class DoorPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    door = models.ForeignKey("Doors", models.DO_NOTHING)
    employee = models.ForeignKey("Employees", models.DO_NOTHING, blank=True, null=True)
    role = models.ForeignKey("Roles", models.DO_NOTHING, blank=True, null=True)
    access_rule = models.ForeignKey("AccessRules", models.DO_NOTHING, blank=True, null=True)
    is_active = models.BooleanField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "door_permissions"


class Doors(models.Model):
    id = models.BigAutoField(primary_key=True)
    door_code = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=250, blank=True, null=True)
    device = models.ForeignKey("Devices", models.DO_NOTHING, blank=True, null=True)
    lock_type = models.CharField(max_length=50, blank=True, null=True)
    unlock_duration_seconds = models.IntegerField()
    sensor_enabled = models.BooleanField()
    exit_button_enabled = models.BooleanField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "doors"


class Employees(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee_number = models.CharField(unique=True, max_length=50)
    user = models.OneToOneField("Users", models.DO_NOTHING, blank=True, null=True)
    department = models.ForeignKey("Departments", models.DO_NOTHING, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    job_title = models.CharField(max_length=150, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    photo_path = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "employees"


class FaceTemplates(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey("Employees", models.DO_NOTHING)
    template_data = models.TextField()
    algorithm = models.CharField(max_length=100, blank=True, null=True)
    confidence_threshold = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "face_templates"


class Fingerprints(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey("Employees", models.DO_NOTHING)
    fingerprint_template = models.TextField()
    finger_name = models.CharField(max_length=50, blank=True, null=True)
    sensor_type = models.CharField(max_length=100, blank=True, null=True)
    fingerprint_index = models.IntegerField(blank=True, null=True)
    quality_score = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "fingerprints"


class Incidents(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey("Employees", models.DO_NOTHING, blank=True, null=True)
    door = models.ForeignKey("Doors", models.DO_NOTHING, blank=True, null=True)
    device = models.ForeignKey("Devices", models.DO_NOTHING, blank=True, null=True)
    incident_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=30)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30)
    reported_at = models.DateTimeField()
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey("Users", models.DO_NOTHING, db_column="resolved_by", blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "incidents"


class Notifications(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey("Users", models.DO_NOTHING, blank=True, null=True)
    employee = models.ForeignKey("Employees", models.DO_NOTHING, blank=True, null=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50)
    is_read = models.BooleanField()
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "notifications"


class Permissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    code = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "permissions"


class RfidCards(models.Model):
    id = models.BigAutoField(primary_key=True)
    card_uid = models.CharField(unique=True, max_length=100)
    employee = models.ForeignKey("Employees", models.DO_NOTHING, blank=True, null=True)
    card_number = models.CharField(unique=True, max_length=100, blank=True, null=True)
    card_type = models.CharField(max_length=50, blank=True, null=True)
    issued_at = models.DateTimeField()
    expires_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "rfid_cards"


class Roles(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "roles"


class Shifts(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    grace_period_minutes = models.IntegerField()
    late_after_minutes = models.IntegerField()
    early_leave_before_minutes = models.IntegerField()
    is_overnight = models.BooleanField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "shifts"


class Users(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=150)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "users"
