from django.db import models
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)


# ============================================================
# EMPLOYEE
# ============================================================

class Employee(models.Model):

    # --------------------------------------------------------
    # DATABASE PRIMARY KEY
    # --------------------------------------------------------

    id = models.BigAutoField(
        primary_key=True
    )

    # --------------------------------------------------------
    # BUSINESS EMPLOYEE ID
    # Must contain 6–8 digits
    # --------------------------------------------------------

    employee_id = models.BigIntegerField(
        unique=True,
        validators=[
            MinValueValidator(
                100000,
                message="Employee ID must contain at least 6 digits.",
            ),
            MaxValueValidator(
                99999999,
                message="Employee ID must contain at most 8 digits.",
            ),
        ],
    )

    # --------------------------------------------------------
    # EMPLOYEE NUMBER
    # Examples:
    # EMP001
    # EMP002
    # EMP003
    # --------------------------------------------------------

    employee_number = models.CharField(
        max_length=50,
        unique=True,
    )

    # --------------------------------------------------------
    # EXISTING DATABASE FIELDS
    # --------------------------------------------------------

    user_id = models.BigIntegerField(
    null=True,
    blank=True,
    )

    department = models.ForeignKey(
    "departments.Department",
    on_delete=models.DO_NOTHING,
    db_column="department_id",
    null=True,
    blank=True,
    related_name="employees",
    )

    first_name = models.CharField(
        max_length=100,
    )

    middle_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    last_name = models.CharField(
        max_length=100,
    )

    gender = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )

    date_of_birth = models.DateField(
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

    address = models.TextField(
        null=True,
        blank=True,
    )

    job_title = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )

    hire_date = models.DateField(
        null=True,
        blank=True,
    )

    photo_path = models.TextField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        default="active",
    )

    created_at = models.DateTimeField()

    updated_at = models.DateTimeField()

    # --------------------------------------------------------
    # EXISTING POSTGRESQL TABLE
    # --------------------------------------------------------

    class Meta:
        managed = False
        db_table = "employees"

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    def __str__(self):
        return (
            f"{self.employee_number} - "
            f"{self.employee_id} - "
            f"{self.first_name} {self.last_name}"
        )

# ============================================================
# RFID CARD
# Existing PostgreSQL table: rfid_cards
# ============================================================

class RFIDCard(models.Model):

    id = models.BigAutoField(
        primary_key=True
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.DO_NOTHING,
        db_column="employee_id",
        null=True,
        blank=True,
        related_name="rfid_cards",
    )

    card_uid = models.CharField(
        max_length=100,
        unique=True,
    )

    card_number = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
    )

    card_type = models.CharField(
        max_length=50,
        default="RFID",
    )

    issued_at = models.DateTimeField()

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        default="active",
    )

    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "rfid_cards"

    def __str__(self):
        employee_name = (
            self.employee.employee_number
            if self.employee
            else "Unassigned"
        )

        return (
            f"{employee_name} - "
            f"{self.card_uid}"
        )

# ============================================================
# FACE TEMPLATE
# Existing PostgreSQL table: face_templates
# ============================================================

class FaceTemplate(models.Model):

    id = models.BigAutoField(
        primary_key=True
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.DO_NOTHING,
        db_column="employee_id",
        related_name="face_templates",
    )

    template_data = models.TextField()

    algorithm = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    confidence_threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=80.00,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        default="active",
    )

    created_at = models.DateTimeField()

    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "face_templates"

    def __str__(self):
        return (
            f"{self.employee.employee_number} - "
            f"Face Template"
        )