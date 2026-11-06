from django.db import models
from employees.models import Employee


class Attendance(models.Model):

    id = models.BigAutoField(primary_key=True)

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="attendance_records",
    )

    attendance_date = models.DateField()

    check_in = models.DateTimeField(
        null=True,
        blank=True,
    )

    check_out = models.DateTimeField(
        null=True,
        blank=True,
    )

    late_minutes = models.IntegerField(
        default=0,
    )

    early_leave_minutes = models.IntegerField(
        default=0,
    )

    worked_minutes = models.IntegerField(
        default=0,
    )

    overtime_minutes = models.IntegerField(
        default=0,
    )

    status = models.CharField(
        max_length=30,
        default="present",
    )

    notes = models.TextField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField()

    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "attendance"
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "attendance_date"],
                name="attendance_employee_date_unique",
            )
        ]

    def __str__(self):
        return f"{self.employee} - {self.attendance_date}"