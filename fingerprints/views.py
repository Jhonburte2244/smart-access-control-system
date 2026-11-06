import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from employees.models import Employee

from .models import Fingerprint


# ============================================================
# FINGERPRINT LIST
# ============================================================

@login_required
def fingerprint_list(request):

    search = request.GET.get("search", "").strip()

    fingerprints = Fingerprint.objects.select_related(
        "employee"
    ).order_by("-created_at")

    if search:

        fingerprints = fingerprints.filter(
            Q(employee__employee_number__icontains=search)
            | Q(employee__first_name__icontains=search)
            | Q(employee__middle_name__icontains=search)
            | Q(employee__last_name__icontains=search)
            | Q(finger_name__icontains=search)
            | Q(sensor_type__icontains=search)
            | Q(status__icontains=search)
        )

    total_fingerprints = fingerprints.count()

    active_fingerprints = fingerprints.filter(
        status__iexact="active"
    ).count()

    inactive_fingerprints = fingerprints.filter(
        status__iexact="inactive"
    ).count()

    context = {
        "fingerprints": fingerprints,
        "search": search,
        "total_fingerprints": total_fingerprints,
        "active_fingerprints": active_fingerprints,
        "inactive_fingerprints": inactive_fingerprints,
    }

    return render(
        request,
        "fingerprints/list.html",
        context,
    )


# ============================================================
# ADD FINGERPRINT
# ============================================================

@login_required
def fingerprint_add(request):

    employees = Employee.objects.order_by(
        "employee_number"
    )

    if request.method == "POST":

        employee_id = request.POST.get(
            "employee_id"
        )

        fingerprint_template = request.POST.get(
            "fingerprint_template",
            ""
        ).strip()

        finger_name = request.POST.get(
            "finger_name",
            ""
        ).strip()

        sensor_type = request.POST.get(
            "sensor_type",
            ""
        ).strip()

        fingerprint_index = request.POST.get(
            "fingerprint_index",
            ""
        ).strip()

        quality_score = request.POST.get(
            "quality_score",
            ""
        ).strip()

        status = request.POST.get(
            "status",
            "active"
        ).strip()

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        if not employee_id:

            messages.error(
                request,
                "Please select an employee."
            )

            return render(
                request,
                "fingerprints/add.html",
                {"employees": employees},
            )

        employee = get_object_or_404(
            Employee,
            id=employee_id,
        )

        if not fingerprint_template:

            messages.error(
                request,
                "Fingerprint template is required."
            )

            return render(
                request,
                "fingerprints/add.html",
                {"employees": employees},
            )

        # ----------------------------------------------------
        # Convert numeric fields
        # ----------------------------------------------------

        fingerprint_index_value = None

        if fingerprint_index:

            try:

                fingerprint_index_value = int(
                    fingerprint_index
                )

            except ValueError:

                messages.error(
                    request,
                    "Fingerprint index must be a number."
                )

                return render(
                    request,
                    "fingerprints/add.html",
                    {"employees": employees},
                )

        quality_score_value = None

        if quality_score:

            try:

                quality_score_value = int(
                    quality_score
                )

            except ValueError:

                messages.error(
                    request,
                    "Quality score must be a number."
                )

                return render(
                    request,
                    "fingerprints/add.html",
                    {"employees": employees},
                )

            if not 0 <= quality_score_value <= 100:

                messages.error(
                    request,
                    "Quality score must be between 0 and 100."
                )

                return render(
                    request,
                    "fingerprints/add.html",
                    {"employees": employees},
                )

        # ----------------------------------------------------
        # Create fingerprint
        # ----------------------------------------------------

        now = timezone.now()

        Fingerprint.objects.create(

            employee=employee,

            fingerprint_template=fingerprint_template,

            finger_name=finger_name or None,

            sensor_type=sensor_type or None,

            fingerprint_index=fingerprint_index_value,

            quality_score=quality_score_value,

            status=status or "active",

            created_at=now,

            updated_at=now,
        )

        messages.success(
            request,
            "Fingerprint added successfully."
        )

        return redirect(
            "fingerprints:fingerprint_list"
        )

    context = {
        "employees": employees,
    }

    return render(
        request,
        "fingerprints/add.html",
        context,
    )


# ============================================================
# FINGERPRINT DETAIL / VIEW
# ============================================================

@login_required
def fingerprint_detail(
    request,
    fingerprint_id,
):

    fingerprint = get_object_or_404(
        Fingerprint.objects.select_related(
            "employee"
        ),
        id=fingerprint_id,
    )

    return render(
        request,
        "fingerprints/detail.html",
        {
            "fingerprint": fingerprint,
        },
    )


# ============================================================
# EDIT FINGERPRINT
# ============================================================

@login_required
def fingerprint_edit(
    request,
    fingerprint_id,
):

    fingerprint = get_object_or_404(
        Fingerprint,
        id=fingerprint_id,
    )

    employees = Employee.objects.order_by(
        "employee_number"
    )

    if request.method == "POST":

        employee_id = request.POST.get(
            "employee_id"
        )

        fingerprint_template = request.POST.get(
            "fingerprint_template",
            ""
        ).strip()

        finger_name = request.POST.get(
            "finger_name",
            ""
        ).strip()

        sensor_type = request.POST.get(
            "sensor_type",
            ""
        ).strip()

        fingerprint_index = request.POST.get(
            "fingerprint_index",
            ""
        ).strip()

        quality_score = request.POST.get(
            "quality_score",
            ""
        ).strip()

        status = request.POST.get(
            "status",
            "active"
        ).strip()

        # ----------------------------------------------------
        # Employee
        # ----------------------------------------------------

        if not employee_id:

            messages.error(
                request,
                "Please select an employee."
            )

            return render(
                request,
                "fingerprints/edit.html",
                {
                    "fingerprint": fingerprint,
                    "employees": employees,
                },
            )

        employee = get_object_or_404(
            Employee,
            id=employee_id,
        )

        # ----------------------------------------------------
        # Template
        # ----------------------------------------------------

        if not fingerprint_template:

            messages.error(
                request,
                "Fingerprint template is required."
            )

            return render(
                request,
                "fingerprints/edit.html",
                {
                    "fingerprint": fingerprint,
                    "employees": employees,
                },
            )

        # ----------------------------------------------------
        # Fingerprint index
        # ----------------------------------------------------

        fingerprint_index_value = None

        if fingerprint_index:

            try:

                fingerprint_index_value = int(
                    fingerprint_index
                )

            except ValueError:

                messages.error(
                    request,
                    "Fingerprint index must be a number."
                )

                return render(
                    request,
                    "fingerprints/edit.html",
                    {
                        "fingerprint": fingerprint,
                        "employees": employees,
                    },
                )

        # ----------------------------------------------------
        # Quality score
        # ----------------------------------------------------

        quality_score_value = None

        if quality_score:

            try:

                quality_score_value = int(
                    quality_score
                )

            except ValueError:

                messages.error(
                    request,
                    "Quality score must be a number."
                )

                return render(
                    request,
                    "fingerprints/edit.html",
                    {
                        "fingerprint": fingerprint,
                        "employees": employees,
                    },
                )

            if not 0 <= quality_score_value <= 100:

                messages.error(
                    request,
                    "Quality score must be between 0 and 100."
                )

                return render(
                    request,
                    "fingerprints/edit.html",
                    {
                        "fingerprint": fingerprint,
                        "employees": employees,
                    },
                )

        # ----------------------------------------------------
        # Update
        # ----------------------------------------------------

        fingerprint.employee = employee

        fingerprint.fingerprint_template = (
            fingerprint_template
        )

        fingerprint.finger_name = (
            finger_name or None
        )

        fingerprint.sensor_type = (
            sensor_type or None
        )

        fingerprint.fingerprint_index = (
            fingerprint_index_value
        )

        fingerprint.quality_score = (
            quality_score_value
        )

        fingerprint.status = (
            status or "active"
        )

        fingerprint.updated_at = timezone.now()

        fingerprint.save(
            force_update=True
        )

        messages.success(
            request,
            "Fingerprint updated successfully."
        )

        return redirect(
            "fingerprints:fingerprint_detail",
            fingerprint_id=fingerprint.id,
        )

    context = {
        "fingerprint": fingerprint,
        "employees": employees,
    }

    return render(
        request,
        "fingerprints/edit.html",
        context,
    )


# ============================================================
# ACTIVATE / DEACTIVATE
# ============================================================

@login_required
def fingerprint_toggle_status(
    request,
    fingerprint_id,
):

    if request.method != "POST":

        return redirect(
            "fingerprints:fingerprint_list"
        )

    fingerprint = get_object_or_404(
        Fingerprint,
        id=fingerprint_id,
    )

    if fingerprint.status.lower() == "active":

        fingerprint.status = "inactive"

        message = (
            "Fingerprint deactivated successfully."
        )

    else:

        fingerprint.status = "active"

        message = (
            "Fingerprint activated successfully."
        )

    fingerprint.updated_at = timezone.now()

    fingerprint.save(
        force_update=True
    )

    messages.success(
        request,
        message,
    )

    return redirect(
        "fingerprints:fingerprint_list"
    )


# ============================================================
# DELETE FINGERPRINT
# ============================================================

@login_required
def fingerprint_delete(
    request,
    fingerprint_id,
):

    if request.method != "POST":

        return redirect(
            "fingerprints:fingerprint_list"
        )

    fingerprint = get_object_or_404(
        Fingerprint,
        id=fingerprint_id,
    )

    fingerprint_name = (
        fingerprint.finger_name
        or "Fingerprint"
    )

    fingerprint.delete()

    messages.success(
        request,
        f"{fingerprint_name} deleted successfully."
    )

    return redirect(
        "fingerprints:fingerprint_list"
    )
 
 
@csrf_exempt
def fingerprint_enroll_api(request):
    """
    API endpoint used by ESP32 / fingerprint device
    to submit a newly captured fingerprint template.
    """

    # ---------------------------------------------------------
    # Only POST is allowed
    # ---------------------------------------------------------
    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Only POST requests are allowed.",
            },
            status=405,
        )

    # ---------------------------------------------------------
    # Read JSON request
    # ---------------------------------------------------------
    try:
        data = json.loads(request.body.decode("utf-8"))

    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid JSON data.",
            },
            status=400,
        )

    # ---------------------------------------------------------
    # Read fields
    # ---------------------------------------------------------
    employee_id = data.get("employee_id")
    finger_name = data.get("finger_name")
    fingerprint_template = data.get("fingerprint_template")
    sensor_type = data.get("sensor_type", "R307")
    fingerprint_index = data.get("fingerprint_index")
    quality_score = data.get("quality_score")
    status = data.get("status", "active")

    # ---------------------------------------------------------
    # Validate required fields
    # ---------------------------------------------------------
    if not employee_id:
        return JsonResponse(
            {
                "success": False,
                "message": "employee_id is required.",
            },
            status=400,
        )

    if not fingerprint_template:
        return JsonResponse(
            {
                "success": False,
                "message": "fingerprint_template is required.",
            },
            status=400,
        )

    if not finger_name:
        return JsonResponse(
            {
                "success": False,
                "message": "finger_name is required.",
            },
            status=400,
        )

    # ---------------------------------------------------------
    # Find employee
    # ---------------------------------------------------------
    try:
        employee = Employee.objects.get(
            id=employee_id
        )

    except Employee.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "message": "Employee not found.",
                "employee_id": employee_id,
            },
            status=404,
        )

    # ---------------------------------------------------------
    # Check whether this employee already has this finger
    # ---------------------------------------------------------
    existing_finger = Fingerprint.objects.filter(
        employee=employee,
        finger_name=finger_name,
        status="active",
    ).first()

    if existing_finger:
        return JsonResponse(
            {
                "success": False,
                "duplicate": True,
                "message": (
                    "This finger is already registered "
                    "for this employee."
                ),
                "fingerprint_id": existing_finger.id,
                "employee_id": employee.employee_id,
                "finger_name": existing_finger.finger_name,
            },
            status=409,
        )

    # ---------------------------------------------------------
    # Create fingerprint record
    # ---------------------------------------------------------
    now = timezone.now()

    fingerprint = Fingerprint(
        employee=employee,
        fingerprint_template=fingerprint_template,
        finger_name=finger_name,
        sensor_type=sensor_type,
        fingerprint_index=fingerprint_index,
        quality_score=quality_score,
        status=status,
        created_at=now,
        updated_at=now,
    )

    # Existing PostgreSQL table is managed=False
    fingerprint.save(force_insert=True)

    # ---------------------------------------------------------
    # Return success
    # ---------------------------------------------------------
    return JsonResponse(
        {
            "success": True,
            "message": "Fingerprint enrolled successfully.",
            "fingerprint": {
                "id": fingerprint.id,
                "employee_id": employee.employee_id,
                "employee_number": employee.employee_number,
                "finger_name": fingerprint.finger_name,
                "sensor_type": fingerprint.sensor_type,
                "fingerprint_index": fingerprint.fingerprint_index,
                "quality_score": fingerprint.quality_score,
                "status": fingerprint.status,
            },
        },
        status=201,
    )