from django.db import models


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ("info", "Information"),
        ("success", "Success"),
        ("warning", "Warning"),
        ("danger", "Danger"),
        ("access", "Access"),
        ("security", "Security"),
        ("system", "System"),
    ]

    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_column="user_id",
        related_name="smac_notifications",
    )

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column="employee_id",
        related_name="notifications",
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        default="info",
    )

    is_read = models.BooleanField(default=False)

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title