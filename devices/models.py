from django.db import models


class Device(models.Model):

    id = models.BigAutoField(primary_key=True)

    device_code = models.CharField(
        max_length=100,
        unique=True,
    )

    device_name = models.CharField(
        max_length=150,
    )

    device_type = models.CharField(
        max_length=50,
        default="ESP32",
    )

    location = models.CharField(
        max_length=250,
        null=True,
        blank=True,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    mac_address = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    firmware_version = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    last_seen = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "devices"
        ordering = ["device_code"]

    def __str__(self):
        return f"{self.device_code} - {self.device_name}"