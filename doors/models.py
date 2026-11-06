
from django.db import models


class Door(models.Model):

    # ============================================================
    # PRIMARY KEY
    # ============================================================

    id = models.BigAutoField(
        primary_key=True,
    )


    # ============================================================
    # DOOR IDENTIFICATION
    # ============================================================

    door_code = models.CharField(
        max_length=100,
        unique=True,
    )

    name = models.CharField(
        max_length=150,
    )


    # ============================================================
    # LOCATION
    # ============================================================

    location = models.CharField(
        max_length=250,
        null=True,
        blank=True,
    )


    # ============================================================
    # LOCK CONFIGURATION
    # ============================================================

    lock_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    unlock_duration_seconds = models.IntegerField(
        default=5,
    )


    # ============================================================
    # DOOR HARDWARE
    # ============================================================

    sensor_enabled = models.BooleanField(
        default=True,
    )

    exit_button_enabled = models.BooleanField(
        default=True,
    )


    # ============================================================
    # STATUS
    # ============================================================

    is_active = models.BooleanField(
        default=True,
    )


    # ============================================================
    # TIMESTAMPS
    # ============================================================

    created_at = models.DateTimeField()

    updated_at = models.DateTimeField()


    # ============================================================
    # DATABASE CONFIGURATION
    # ============================================================

    class Meta:

        # IMPORTANT:
        # The PostgreSQL table already exists.
        # Django must NOT create, modify, or delete it.

        managed = False

        db_table = "doors"


    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return f"{self.door_code} - {self.name}"

