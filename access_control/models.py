from django.db import models
from django.contrib.auth.decorators import login_required
from django.shortcuts import render




class AccessRule(models.Model):
    id = models.BigAutoField(primary_key=True)

    name = models.CharField(max_length=150, unique=True)

    description = models.TextField(
        null=True,
        blank=True,
    )

    access_type = models.CharField(
        max_length=30,
    )

    start_time = models.TimeField(
        null=True,
        blank=True,
    )

    end_time = models.TimeField(
        null=True,
        blank=True,
    )

    valid_from = models.DateField(
        null=True,
        blank=True,
    )

    valid_until = models.DateField(
        null=True,
        blank=True,
    )

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

    def __str__(self):
        return self.name

class DoorPermission(models.Model):

    id = models.BigAutoField(
        primary_key=True
    )

    door = models.ForeignKey(
        "doors.Door",
        on_delete=models.DO_NOTHING,
        db_column="door_id",
        related_name="permissions",
    )

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.DO_NOTHING,
        db_column="employee_id",
        null=True,
        blank=True,
        related_name="door_permissions",
    )

    role = models.ForeignKey(
        "access_control.Role",
        on_delete=models.DO_NOTHING,
        db_column="role_id",
        null=True,
        blank=True,
        related_name="door_permissions",
    )

    access_rule = models.ForeignKey(
        "access_control.AccessRule",
        on_delete=models.DO_NOTHING,
        db_column="access_rule_id",
        null=True,
        blank=True,
        related_name="door_permissions",
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "door_permissions"

    def __str__(self):

        if self.employee:
            subject = self.employee.employee_number

        elif self.role:
            subject = self.role.name

        else:
            subject = "Unassigned"

        return f"{subject} → {self.door.name}"

        
class Role(models.Model):
    id = models.BigAutoField(
        primary_key=True,
    )

    name = models.CharField(
        max_length=100,
    )

    description = models.TextField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField()

    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "roles"

    def __str__(self):
        return self.name
        
@login_required
def doors(request):
    door_list = Door.objects.all().order_by("name")

    return render(
        request,
        "dashboard/doors.html",
        {
            "doors": door_list,
        },
    )



class AccessLog(models.Model):

    id = models.BigAutoField(
        primary_key=True,
    )

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.DO_NOTHING,
        db_column="employee_id",
        null=True,
        blank=True,
        related_name="access_logs",
    )

    door = models.ForeignKey(
        "doors.Door",
        on_delete=models.DO_NOTHING,
        db_column="door_id",
        null=True,
        blank=True,
        related_name="access_logs",
    )

    rfid_card = models.ForeignKey(
        "employees.RFIDCard",
        on_delete=models.DO_NOTHING,
        db_column="rfid_card_id",
        null=True,
        blank=True,
        related_name="access_logs",
    )

    authentication_method = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    action = models.CharField(
        max_length=30,
    )

    reason = models.TextField(
        null=True,
        blank=True,
    )

    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    event_time = models.DateTimeField()

    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "access_logs"
        ordering = ["-event_time"]

    def __str__(self):
        employee_name = (
            self.employee.employee_number
            if self.employee
            else "Unknown Employee"
        )

        door_name = (
            self.door.name
            if self.door
            else "Unknown Door"
        )

        return (
            f"{employee_name} → "
            f"{door_name} → "
            f"{self.action}"
        )