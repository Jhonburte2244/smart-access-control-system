from django.db import models

from employees.models import Employee


class Fingerprint(models.Model):

    id = models.BigAutoField(
        primary_key=True
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.DO_NOTHING,
        db_column="employee_id",
        related_name="fingerprints",
    )

    fingerprint_template = models.TextField()

    finger_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    sensor_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    fingerprint_index = models.IntegerField(
        null=True,
        blank=True,
    )

    quality_score = models.IntegerField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
    )

    created_at = models.DateTimeField()

    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "fingerprints"

    def __str__(self):
        employee_name = (
            self.employee.employee_number
            if self.employee
            else "Unassigned"
        )

        return f"{employee_name} - {self.finger_name or 'Fingerprint'}"