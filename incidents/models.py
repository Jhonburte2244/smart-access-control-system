from django.db import models


class Incident(models.Model):
    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("investigating", "Investigating"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    id = models.BigAutoField(primary_key=True)

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="employee_id",
        related_name="incidents",
    )

    door = models.ForeignKey(
        "doors.Door",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="door_id",
        related_name="incidents",
    )

    incident_type = models.CharField(max_length=100)

    severity = models.CharField(
        max_length=30,
        choices=SEVERITY_CHOICES,
        default="medium",
    )

    description = models.TextField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="open",
    )

    reported_at = models.DateTimeField()

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    resolved_by = models.BigIntegerField(
        null=True,
        blank=True,
        db_column="resolved_by",
    )

    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "incidents"
        ordering = ["-reported_at"]

    def __str__(self):
        return f"{self.incident_type} - {self.severity}"