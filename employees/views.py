from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db import transaction
from departments.models import Department

from .models import (
    Employee,
    RFIDCard,
    FaceTemplate,
)
from fingerprints.models import Fingerprint

# =========================================================
# EMPLOYEE LIST
# =========================================================

def employees(request):

    employee_list = Employee.objects.all().order_by("-id")

    search = request.GET.get(
        "search",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    if search:

        employee_list = (
            employee_list.filter(
                employee_id__icontains=search
            )
            | employee_list.filter(
                employee_number__icontains=search
            )
            | employee_list.filter(
                first_name__icontains=search
            )
            | employee_list.filter(
                middle_name__icontains=search
            )
            | employee_list.filter(
                last_name__icontains=search
            )
            | employee_list.filter(
                phone__icontains=search
            )
            | employee_list.filter(
                email__icontains=search
            )
        )

    if status:

        employee_list = employee_list.filter(
            status=status
        )

    context = {
        "employees": employee_list,
        "search": search,
        "selected_status": status,

        "total_employees": Employee.objects.count(),

        "active_employees": Employee.objects.filter(
            status="active"
        ).count(),

        "inactive_employees": Employee.objects.exclude(
            status="active"
        ).count(),
    }

    return render(
        request,
        "dashboard/employees.html",
        context,
    )


# =========================================================
# GENERATE EMPLOYEE NUMBER
#
# EMP001
# EMP002
# EMP003
# ...
# =========================================================

def generate_employee_number():

    last_employee = (
        Employee.objects
        .filter(
            employee_number__startswith="EMP"
        )
        .order_by("-id")
        .first()
    )

    if not last_employee:
        return "EMP001"

    try:

        last_number = int(
            last_employee.employee_number.replace(
                "EMP",
                "",
            )
        )

    except (
        ValueError,
        AttributeError,
    ):

        last_number = 0

    return f"EMP{last_number + 1:03d}"


# =========================================================
# VALIDATE EMPLOYEE ID
#
# Must be 6–8 digits
# =========================================================

def validate_employee_id(employee_id):

    if not employee_id:
        return "Employee ID is required."

    if not employee_id.isdigit():
        return "Employee ID must contain numbers only."

    if len(employee_id) < 6:
        return "Employee ID must contain at least 6 digits."

    if len(employee_id) > 8:
        return "Employee ID must contain at most 8 digits."

    return None


# =========================================================
# ADD EMPLOYEE
# =========================================================

def employee_add(request):

    if request.method == "POST":

        # =====================================================
        # EMPLOYEE INFORMATION
        # =====================================================

        employee_id = request.POST.get(
            "employee_id",
            "",
        ).strip()

        first_name = request.POST.get(
            "first_name",
            "",
        ).strip()

        middle_name = request.POST.get(
            "middle_name",
            "",
        ).strip()

        last_name = request.POST.get(
            "last_name",
            "",
        ).strip()

        # =====================================================
        # VALIDATE EMPLOYEE ID
        # =====================================================

        error = validate_employee_id(
            employee_id
        )

        if error:

            messages.error(
                request,
                error,
            )

            return redirect(
                "employees:employee_add"
            )

        # =====================================================
        # CHECK DUPLICATE EMPLOYEE ID
        # =====================================================

        if Employee.objects.filter(
            employee_id=int(employee_id)
        ).exists():

            messages.error(
                request,
                "An employee with this Employee ID already exists.",
            )

            return redirect(
                "employees:employee_add"
            )

        # =====================================================
        # VALIDATE FIRST NAME
        # =====================================================

        if not first_name:

            messages.error(
                request,
                "First name is required.",
            )

            return redirect(
                "employees:employee_add"
            )

        # =====================================================
        # VALIDATE LAST NAME
        # =====================================================

        if not last_name:

            messages.error(
                request,
                "Last name is required.",
            )

            return redirect(
                "employees:employee_add"
            )
            

        # =========================================================
        # GET REQUEST
        # =========================================================

        departments = Department.objects.filter(
             is_active=True
        ).order_by("name")

        return render(
                request,
                "employees/employee_form.html",
                {
                "page_title": "Add Employee",
                "submit_text": "Add Employee",
                "departments": departments,
                },
        )


        # =====================================================
        # GENERATE EMPLOYEE NUMBER
        # =====================================================

        employee_number = generate_employee_number()

        # =====================================================
        # CURRENT TIME
        # =====================================================

        now = timezone.now()

        # =====================================================
        # AUTHENTICATION DATA
        #
        # These fields will come from the employee form.
        # They are OPTIONAL during this first implementation.
        # =====================================================

        # -----------------------------------------------------
        # FINGERPRINT
        # -----------------------------------------------------

        fingerprint_template = request.POST.get(
            "fingerprint_template",
            "",
        ).strip()

        finger_name = request.POST.get(
            "finger_name",
            "",
        ).strip()

        sensor_type = request.POST.get(
            "sensor_type",
            "",
        ).strip()

        fingerprint_index = request.POST.get(
            "fingerprint_index",
            "",
        ).strip()

        quality_score = request.POST.get(
            "quality_score",
            "",
        ).strip()

        # -----------------------------------------------------
        # RFID
        # -----------------------------------------------------

        card_uid = request.POST.get(
            "card_uid",
            "",
        ).strip()

        card_number = request.POST.get(
            "card_number",
            "",
        ).strip()

        card_type = request.POST.get(
            "card_type",
            "RFID",
        ).strip()

        # -----------------------------------------------------
        # FACE
        # -----------------------------------------------------

        face_template_data = request.POST.get(
            "face_template_data",
            "",
        ).strip()

        face_algorithm = request.POST.get(
            "face_algorithm",
            "",
        ).strip()

        face_confidence = request.POST.get(
            "face_confidence_threshold",
            "",
        ).strip()

        # =====================================================
        # VALIDATE FINGERPRINT
        # =====================================================

        fingerprint_index_value = None

        if fingerprint_index:

            try:

                fingerprint_index_value = int(
                    fingerprint_index
                )

            except ValueError:

                messages.error(
                    request,
                    "Fingerprint index must be a valid number.",
                )

                return redirect(
                    "employees:employee_add"
                )

        quality_score_value = None

        if quality_score:

            try:

                quality_score_value = int(
                    quality_score
                )

                if not 0 <= quality_score_value <= 100:

                    messages.error(
                        request,
                        "Fingerprint quality score must be between 0 and 100.",
                    )

                    return redirect(
                        "employees:employee_add"
                    )

            except ValueError:

                messages.error(
                    request,
                    "Fingerprint quality score must be a valid number.",
                )

                return redirect(
                    "employees:employee_add"
                )

        # =====================================================
        # VALIDATE RFID
        # =====================================================

        if card_uid:

            if RFIDCard.objects.filter(
                card_uid=card_uid
            ).exists():

                messages.error(
                    request,
                    "This RFID card UID is already registered.",
                )

                return redirect(
                    "employees:employee_add"
                )

        if card_number:

            if RFIDCard.objects.filter(
                card_number=card_number
            ).exists():

                messages.error(
                    request,
                    "This RFID card number is already registered.",
                )

                return redirect(
                    "employees:employee_add"
                )

        # =====================================================
        # CREATE EMPLOYEE + AUTHENTICATION DATA
        #
        # transaction.atomic() means:
        #
        # Employee creation
        # +
        # Fingerprint
        # +
        # RFID
        # +
        # Face
        #
        # are treated as one operation.
        # =====================================================

        try:

            with transaction.atomic():

                # =================================================
                # CREATE EMPLOYEE
                # =================================================

                employee = Employee.objects.create(

                    employee_id=int(
                        employee_id
                    ),

                    employee_number=employee_number,

                    user_id=request.POST.get(
                        "user_id"
                    ) or None,

                    department_id=request.POST.get(
                        "department_id"
                    ) or None,

                    first_name=first_name,

                    middle_name=middle_name or None,

                    last_name=last_name,

                    gender=request.POST.get(
                        "gender"
                    ) or None,

                    date_of_birth=request.POST.get(
                        "date_of_birth"
                    ) or None,

                    phone=request.POST.get(
                        "phone"
                    ) or None,

                    email=request.POST.get(
                        "email"
                    ) or None,

                    address=request.POST.get(
                        "address"
                    ) or None,

                    job_title=request.POST.get(
                        "job_title"
                    ) or None,

                    hire_date=request.POST.get(
                        "hire_date"
                    ) or None,

                    photo_path=request.POST.get(
                        "photo_path"
                    ) or None,

                    status=request.POST.get(
                        "status"
                    ) or "active",

                    created_at=now,

                    updated_at=now,
                )

                # =================================================
                # CREATE FINGERPRINT
                # =================================================

                if fingerprint_template:

                    Fingerprint.objects.create(

                        employee=employee,

                        fingerprint_template=(
                            fingerprint_template
                        ),

                        finger_name=(
                            finger_name or None
                        ),

                        sensor_type=(
                            sensor_type or None
                        ),

                        fingerprint_index=(
                            fingerprint_index_value
                        ),

                        quality_score=(
                            quality_score_value
                        ),

                        status="active",

                        created_at=now,

                        updated_at=now,
                    )

                # =================================================
                # CREATE RFID CARD
                # =================================================

                if card_uid:

                    RFIDCard.objects.create(

                        employee=employee,

                        card_uid=card_uid,

                        card_number=(
                            card_number or None
                        ),

                        card_type=(
                            card_type or "RFID"
                        ),

                        issued_at=now,

                        expires_at=None,

                        status="active",

                        created_at=now,
                    )

                # =================================================
                # CREATE FACE TEMPLATE
                # =================================================

                if face_template_data:

                    confidence_value = 80.00

                    if face_confidence:

                        try:

                            confidence_value = float(
                                face_confidence
                            )

                        except ValueError:

                            messages.error(
                                request,
                                "Face confidence threshold must be a valid number.",
                            )

                            raise ValueError(
                                "Invalid face confidence threshold."
                            )

                    FaceTemplate.objects.create(

                        employee=employee,

                        template_data=(
                            face_template_data
                        ),

                        algorithm=(
                            face_algorithm or None
                        ),

                        confidence_threshold=(
                            confidence_value
                        ),

                        status="active",

                        created_at=now,

                        updated_at=now,
                    )

        except Exception as exc:

            messages.error(
                request,
                f"Employee registration failed: {exc}",
            )

            return redirect(
                "employees:employee_add"
            )

        # =====================================================
        # SUCCESS
        # =====================================================

        messages.success(
            request,
            f"Employee created successfully. "
            f"Employee Number: {employee_number}, "
            f"Employee ID: {employee.employee_id}",
        )

        return redirect(
            "employees:employee_detail",
            employee_id=employee.id,
        )

    # =========================================================
    # GET REQUEST
    # =========================================================

    return render(
        request,
        "employees/employee_form.html",
        {
            "page_title": "Add Employee",
            "submit_text": "Add Employee",
        },
    )


# =========================================================
# EMPLOYEE DETAIL
# =========================================================

def employee_detail(
    request,
    employee_id,
):

    employee = get_object_or_404(
        Employee,
        id=employee_id,
    )

    # =========================================================
    # AUTHENTICATION INFORMATION
    # =========================================================

    fingerprints = employee.fingerprints.all()

    rfid_cards = employee.rfid_cards.all()

    face_templates = employee.face_templates.all()

    return render(
        request,
        "employees/employee_detail.html",
        {
            "employee": employee,

            "fingerprints": fingerprints,

            "rfid_cards": rfid_cards,

            "face_templates": face_templates,
        },
    )


# =========================================================
# EDIT EMPLOYEE
# =========================================================

def employee_edit(
    request,
    employee_id,
):

    employee = get_object_or_404(
        Employee,
        id=employee_id,
    )

    if request.method == "POST":

        new_employee_id = request.POST.get(
            "employee_id",
            "",
        ).strip()

        first_name = request.POST.get(
            "first_name",
            "",
        ).strip()

        last_name = request.POST.get(
            "last_name",
            "",
        ).strip()

        # =====================================================
        # VALIDATE EMPLOYEE ID
        # =====================================================

        error = validate_employee_id(
            new_employee_id
        )

        if error:

            messages.error(
                request,
                error,
            )

            return redirect(
                "employees:employee_edit",
                employee_id=employee.id,
            )

        # =====================================================
        # CHECK DUPLICATE EMPLOYEE ID
        # =====================================================

        duplicate = (
            Employee.objects
            .filter(
                employee_id=int(
                    new_employee_id
                )
            )
            .exclude(
                id=employee.id
            )
            .exists()
        )

        if duplicate:

            messages.error(
                request,
                "Another employee already uses this Employee ID.",
            )

            return redirect(
                "employees:employee_edit",
                employee_id=employee.id,
            )

        # =====================================================
        # VALIDATE FIRST NAME
        # =====================================================

        if not first_name:

            messages.error(
                request,
                "First name is required.",
            )

            return redirect(
                "employees:employee_edit",
                employee_id=employee.id,
            )

        # =====================================================
        # VALIDATE LAST NAME
        # =====================================================

        if not last_name:

            messages.error(
                request,
                "Last name is required.",
            )

            return redirect(
                "employees:employee_edit",
                employee_id=employee.id,
            )

        # =====================================================
        # UPDATE EMPLOYEE
        # =====================================================

        employee.employee_id = int(
            new_employee_id
        )

        employee.first_name = first_name

        employee.middle_name = (
            request.POST.get(
                "middle_name"
            )
            or None
        )

        employee.last_name = last_name

        employee.gender = (
            request.POST.get(
                "gender"
            )
            or None
        )

        employee.date_of_birth = (
            request.POST.get(
                "date_of_birth"
            )
            or None
        )

        employee.phone = (
            request.POST.get(
                "phone"
            )
            or None
        )

        employee.email = (
            request.POST.get(
                "email"
            )
            or None
        )

        employee.address = (
            request.POST.get(
                "address"
            )
            or None
        )

        employee.job_title = (
            request.POST.get(
                "job_title"
            )
            or None
        )

        employee.hire_date = (
            request.POST.get(
                "hire_date"
            )
            or None
        )

        employee.photo_path = (
            request.POST.get(
                "photo_path"
            )
            or None
        )

        employee.status = (
            request.POST.get(
                "status"
            )
            or "active"
        )

        employee.department_id = (
            request.POST.get(
                "department_id"
            )
            or None
        )

        employee.updated_at = timezone.now()

        employee.save()

        # =====================================================
        # SUCCESS
        # =====================================================

        messages.success(
            request,
            "Employee updated successfully.",
        )

        return redirect(
            "employees:employee_detail",
            employee_id=employee.id,
        )

    # =========================================================
    # GET REQUEST
    # =========================================================
    departments = Department.objects.filter( 
                is_active=True 
    ).order_by("name")

    return render(
        request,
        "employees/employee_form.html",
        {
            "employee": employee,
            "page_title": "Edit Employee",
            "submit_text": "Save Changes",
            "departments": departments,
        },
    )


# =========================================================
# DELETE EMPLOYEE
# =========================================================

def employee_delete(
    request,
    employee_id,
):

    employee = get_object_or_404(
        Employee,
        id=employee_id,
    )

    if request.method == "POST":

        employee.delete()

        messages.success(
            request,
            "Employee deleted successfully.",
        )

        return redirect(
            "employees:employees"
        )

    return render(
        request,
        "employees/employee_delete.html",
        {
            "employee": employee,
        },
    )