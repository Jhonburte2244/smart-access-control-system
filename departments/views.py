from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Department
from employees.models import Employee


@login_required
def department_list(request):
    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    departments = Department.objects.all()

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------
    if search:
        departments = departments.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(manager_name__icontains=search)
            | Q(phone__icontains=search)
            | Q(email__icontains=search)
        )

    # ---------------------------------------------------------
    # STATUS FILTER
    # ---------------------------------------------------------
    if status == "active":
        departments = departments.filter(is_active=True)

    elif status == "inactive":
        departments = departments.filter(is_active=False)

    departments = departments.order_by("name")

    # ---------------------------------------------------------
    # EMPLOYEE COUNTS
    # ---------------------------------------------------------
    department_data = []

    for department in departments:

        employee_count = Employee.objects.filter(
            department_id=department.id
        ).count()

        department_data.append(
            {
                "department": department,
                "employee_count": employee_count,
            }
        )

    # ---------------------------------------------------------
    # STATISTICS
    # ---------------------------------------------------------
    total_departments = Department.objects.count()

    active_departments = Department.objects.filter(
        is_active=True
    ).count()

    inactive_departments = Department.objects.filter(
        is_active=False
    ).count()

    return render(
        request,
        "departments/list.html",
        {
            "department_data": department_data,
            "total_departments": total_departments,
            "active_departments": active_departments,
            "inactive_departments": inactive_departments,
            "search": search,
            "selected_status": status,
        },
    )


@login_required
def department_add(request):

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        manager_name = request.POST.get("manager_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()

        # -----------------------------------------------------
        # VALIDATION
        # -----------------------------------------------------

        if not name:

            messages.error(
                request,
                "Department name is required.",
            )

            return render(
                request,
                "departments/add.html",
            )

        # -----------------------------------------------------
        # DUPLICATE CHECK
        # -----------------------------------------------------

        if Department.objects.filter(
            name__iexact=name
        ).exists():

            messages.error(
                request,
                "A department with this name already exists.",
            )

            return render(
                request,
                "departments/add.html",
                {
                    "name": name,
                    "description": description,
                    "manager_name": manager_name,
                    "phone": phone,
                    "email": email,
                },
            )

        # -----------------------------------------------------
        # CURRENT DATE/TIME
        # -----------------------------------------------------

        now = timezone.now()

        # -----------------------------------------------------
        # CREATE DEPARTMENT
        # -----------------------------------------------------

        Department.objects.create(
            name=name,
            description=description or None,
            manager_name=manager_name or None,
            phone=phone or None,
            email=email or None,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        messages.success(
            request,
            f"Department '{name}' was added successfully.",
        )

        return redirect(
            "departments:department_list"
        )

    return render(
        request,
        "departments/add.html",
    )
    
    

@login_required
def department_detail(request, department_id):

    department = get_object_or_404(
        Department,
        id=department_id,
    )

    # ---------------------------------------------------------
    # EMPLOYEES IN THIS DEPARTMENT
    # ---------------------------------------------------------
    employees = Employee.objects.filter(
        department_id=department.id
    ).order_by(
        "first_name",
        "last_name",
    )

    employee_count = employees.count()

    return render(
        request,
        "departments/detail.html",
        {
            "department": department,
            "employees": employees,
            "employee_count": employee_count,
        },
    )


@login_required
def department_edit(request, department_id):

    department = get_object_or_404(
        Department,
        id=department_id,
    )

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        manager_name = request.POST.get("manager_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()

        # -----------------------------------------------------
        # VALIDATION
        # -----------------------------------------------------
        if not name:

            messages.error(
                request,
                "Department name is required.",
            )

            return render(
                request,
                "departments/edit.html",
                {
                    "department": department,
                },
            )

        # -----------------------------------------------------
        # DUPLICATE CHECK
        # -----------------------------------------------------
        duplicate = (
            Department.objects
            .filter(name__iexact=name)
            .exclude(id=department.id)
            .exists()
        )

        if duplicate:

            messages.error(
                request,
                "Another department with this name already exists.",
            )

            return render(
                request,
                "departments/edit.html",
                {
                    "department": department,
                },
            )

        # -----------------------------------------------------
        # UPDATE
        # -----------------------------------------------------
        department.name = name
        department.description = description or None
        department.manager_name = manager_name or None
        department.phone = phone or None
        department.email = email or None

        department.save(
            update_fields=[
                "name",
                "description",
                "manager_name",
                "phone",
                "email",
            ]
        )

        messages.success(
            request,
            f"Department '{name}' was updated successfully.",
        )

        return redirect(
            "departments:department_detail",
            department_id=department.id,
        )

    return render(
        request,
        "departments/edit.html",
        {
            "department": department,
        },
    )


@login_required
def department_toggle_status(
    request,
    department_id,
):

    department = get_object_or_404(
        Department,
        id=department_id,
    )

    if request.method == "POST":

        department.is_active = not department.is_active

        department.save(
            update_fields=["is_active"]
        )

        if department.is_active:

            messages.success(
                request,
                f"'{department.name}' has been activated.",
            )

        else:

            messages.warning(
                request,
                f"'{department.name}' has been deactivated.",
            )

    return redirect(
        "departments:department_list"
    )


@login_required
def department_delete(
    request,
    department_id,
):

    department = get_object_or_404(
        Department,
        id=department_id,
    )

    # ---------------------------------------------------------
    # PREVENT ACCIDENTAL DELETE OF DEPARTMENTS WITH EMPLOYEES
    # ---------------------------------------------------------
    employee_count = Employee.objects.filter(
        department_id=department.id
    ).count()

    if request.method == "POST":

        if employee_count > 0:

            messages.error(
                request,
                (
                    f"Cannot delete '{department.name}' "
                    f"because it has {employee_count} "
                    f"employee(s) assigned to it."
                ),
            )

            return redirect(
                "departments:department_list"
            )

        department_name = department.name

        department.delete()

        messages.success(
            request,
            (
                f"Department '{department_name}' "
                "was deleted successfully."
            ),
        )

        return redirect(
            "departments:department_list"
        )

    return render(
        request,
        "departments/delete.html",
        {
            "department": department,
            "employee_count": employee_count,
        },
    )