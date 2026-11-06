from django.db import models


class Department(models.Model):

    id = models.BigAutoField(primary_key=True)

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    description = models.TextField(
        null=True,
        blank=True,
    )

    manager_name = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )

    phone = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )

    email = models.CharField(
        max_length=150,
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
        db_table = "departments"

    def __str__(self):
        return self.name