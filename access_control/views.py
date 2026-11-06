import json
import csv
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fingerprints.models import Fingerprint
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required


from .models import (
    AccessLog,
    AccessRule,
    DoorPermission,
    Role,
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from doors.models import Door
from employees.models import Employee
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm


# ============================================================
# ACCESS RULES
# ============================================================

@login_required
def access_rule_list(request):
    """
    Display all access rules.
    """

    rules = AccessRule.objects.all().order_by(
        "-priority",
        "name",
    )

    allow_rules = rules.filter(
        access_type__iexact="allow"
    ).count()

    deny_rules = rules.filter(
        access_type__iexact="deny"
    ).count()

    active_rules = rules.filter(
        is_active=True
    ).count()

    inactive_rules = rules.filter(
        is_active=False
    ).count()

    context = {
        "rules": rules,
        "total_rules": rules.count(),
        "allow_rules": allow_rules,
        "deny_rules": deny_rules,
        "active_rules": active_rules,
        "inactive_rules": inactive_rules,
    }

    return render(
        request,
        "access_control/rules.html",
        context,
    )


@login_required
def access_rule_add(request):
    """
    Create a new access rule.
    """

    if request.method == "POST":

        name = request.POST.get(
            "name",
            "",
        ).strip()

        description = request.POST.get(
            "description",
            "",
        ).strip()

        access_type = request.POST.get(
            "access_type",
            "allow",
        ).strip().lower()

        start_time = request.POST.get(
            "start_time"
        ) or None

        end_time = request.POST.get(
            "end_time"
        ) or None

        valid_from = request.POST.get(
            "valid_from"
        ) or None

        valid_until = request.POST.get(
            "valid_until"
        ) or None

        priority = request.POST.get(
            "priority",
            "1",
        ).strip()

        is_active = (
            request.POST.get("is_active")
            == "on"
        )

        # --------------------------------------------------------
        # VALIDATE NAME
        # --------------------------------------------------------

        if not name:

            messages.error(
                request,
                "Rule name is required.",
            )

            return render(
                request,
                "access_control/add.html",
            )

        # --------------------------------------------------------
        # VALIDATE ACCESS TYPE
        # --------------------------------------------------------

        if access_type not in [
            "allow",
            "deny",
        ]:

            messages.error(
                request,
                "Access type must be Allow or Deny.",
            )

            return render(
                request,
                "access_control/add.html",
            )

        # --------------------------------------------------------
        # VALIDATE PRIORITY
        # --------------------------------------------------------

        try:
            priority = int(priority)

        except ValueError:

            messages.error(
                request,
                "Priority must be a valid number.",
            )

            return render(
                request,
                "access_control/add.html",
            )

        # --------------------------------------------------------
        # DAYS
        # --------------------------------------------------------

        monday = (
            request.POST.get("monday")
            == "on"
        )

        tuesday = (
            request.POST.get("tuesday")
            == "on"
        )

        wednesday = (
            request.POST.get("wednesday")
            == "on"
        )

        thursday = (
            request.POST.get("thursday")
            == "on"
        )

        friday = (
            request.POST.get("friday")
            == "on"
        )

        saturday = (
            request.POST.get("saturday")
            == "on"
        )

        sunday = (
            request.POST.get("sunday")
            == "on"
        )

        # --------------------------------------------------------
        # CREATE
        # --------------------------------------------------------

        try:

            AccessRule.objects.create(
                name=name,
                description=description or None,
                access_type=access_type,
                start_time=start_time,
                end_time=end_time,
                valid_from=valid_from,
                valid_until=valid_until,
                monday=monday,
                tuesday=tuesday,
                wednesday=wednesday,
                thursday=thursday,
                friday=friday,
                saturday=saturday,
                sunday=sunday,
                priority=priority,
                is_active=is_active,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )

            messages.success(
                request,
                "Access rule created successfully.",
            )

            return redirect(
                "access_control:access_rules"
            )

        except Exception as exc:

            messages.error(
                request,
                f"Unable to create access rule: {exc}",
            )

    return render(
        request,
        "access_control/add.html",
    )


@login_required
def access_rule_edit(request, rule_id):

    rule = get_object_or_404(
        AccessRule,
        id=rule_id
    )

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        access_type = request.POST.get(
            "access_type",
            "allow"
        ).strip().lower()

        start_time = request.POST.get(
            "start_time"
        ) or None

        end_time = request.POST.get(
            "end_time"
        ) or None

        valid_from = request.POST.get(
            "valid_from"
        ) or None

        valid_until = request.POST.get(
            "valid_until"
        ) or None

        priority = request.POST.get(
            "priority",
            "1"
        ).strip()

        monday = request.POST.get("monday") == "on"
        tuesday = request.POST.get("tuesday") == "on"
        wednesday = request.POST.get("wednesday") == "on"
        thursday = request.POST.get("thursday") == "on"
        friday = request.POST.get("friday") == "on"
        saturday = request.POST.get("saturday") == "on"
        sunday = request.POST.get("sunday") == "on"

        is_active = request.POST.get(
            "is_active"
        ) == "on"

        errors = []

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not name:
            errors.append(
                "Rule name is required."
            )

        if access_type not in [
            "allow",
            "deny",
        ]:
            errors.append(
                "Access type must be Allow or Deny."
            )

        try:
            priority_value = int(priority)

            if priority_value < 1:
                errors.append(
                    "Priority must be at least 1."
                )

        except (TypeError, ValueError):

            priority_value = 1

            errors.append(
                "Priority must be a valid number."
            )

        # ----------------------------------------------------
        # DUPLICATE NAME
        # ----------------------------------------------------

        duplicate_rule = (
            AccessRule.objects
            .filter(name__iexact=name)
            .exclude(id=rule.id)
            .exists()
        )

        if duplicate_rule:

            errors.append(
                "Another access rule with this name already exists."
            )

        # ----------------------------------------------------
        # DATE VALIDATION
        # ----------------------------------------------------

        if (
            valid_from
            and valid_until
            and valid_from > valid_until
        ):

            errors.append(
                "Valid Until cannot be earlier than Valid From."
            )

        # ----------------------------------------------------
        # TIME VALIDATION
        # ----------------------------------------------------

        if (
            start_time
            and end_time
            and start_time > end_time
        ):

            errors.append(
                "End Time cannot be earlier than Start Time."
            )

        # ----------------------------------------------------
        # FORM DATA FOR REDISPLAY
        # ----------------------------------------------------

        form_data = {
            "name": name,
            "description": description,
            "access_type": access_type,
            "start_time": start_time or "",
            "end_time": end_time or "",
            "valid_from": valid_from or "",
            "valid_until": valid_until or "",
            "priority": priority,
            "monday": monday,
            "tuesday": tuesday,
            "wednesday": wednesday,
            "thursday": thursday,
            "friday": friday,
            "saturday": saturday,
            "sunday": sunday,
            "is_active": is_active,
            "all_day": (
                start_time == "00:00"
                and end_time == "23:59"
            ),
        }

        if errors:

            return render(
                request,
                "access_control/add.html",
                {
                    "form_data": form_data,
                    "errors": errors,
                    "edit_mode": True,
                    "rule": rule,
                },
            )

        # ----------------------------------------------------
        # UPDATE
        # ----------------------------------------------------

        try:

            rule.name = name
            rule.description = (
                description or None
            )
            rule.access_type = access_type
            rule.start_time = start_time
            rule.end_time = end_time
            rule.valid_from = valid_from
            rule.valid_until = valid_until

            rule.monday = monday
            rule.tuesday = tuesday
            rule.wednesday = wednesday
            rule.thursday = thursday
            rule.friday = friday
            rule.saturday = saturday
            rule.sunday = sunday

            rule.priority = priority_value
            rule.is_active = is_active
            rule.updated_at = timezone.now()

            rule.save(
                update_fields=[
                    "name",
                    "description",
                    "access_type",
                    "start_time",
                    "end_time",
                    "valid_from",
                    "valid_until",
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                    "priority",
                    "is_active",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                f"Access rule '{rule.name}' was updated successfully."
            )

            return redirect(
                "access_control:access_rules"
            )

        except Exception as exc:

            messages.error(
                request,
                f"Unable to update access rule: {exc}"
            )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    form_data = {
        "name": rule.name,
        "description": rule.description or "",
        "access_type": rule.access_type,
        "start_time": (
            rule.start_time.strftime("%H:%M")
            if rule.start_time
            else ""
        ),
        "end_time": (
            rule.end_time.strftime("%H:%M")
            if rule.end_time
            else ""
        ),
        "valid_from": (
            rule.valid_from.strftime("%Y-%m-%d")
            if rule.valid_from
            else ""
        ),
        "valid_until": (
            rule.valid_until.strftime("%Y-%m-%d")
            if rule.valid_until
            else ""
        ),
        "monday": rule.monday,
        "tuesday": rule.tuesday,
        "wednesday": rule.wednesday,
        "thursday": rule.thursday,
        "friday": rule.friday,
        "saturday": rule.saturday,
        "sunday": rule.sunday,
        "priority": rule.priority,
        "is_active": rule.is_active,
        "all_day": (
            rule.start_time
            and rule.end_time
            and rule.start_time.strftime("%H:%M") == "00:00"
            and rule.end_time.strftime("%H:%M") == "23:59"
        ),
    }

    return render(
        request,
        "access_control/add.html",
        {
            "form_data": form_data,
            "edit_mode": True,
            "rule": rule,
        },
    )

@login_required
def access_rule_toggle_status(
    request,
    rule_id,
):
    """
    Activate/deactivate an access rule.
    """

    rule = get_object_or_404(
        AccessRule,
        id=rule_id,
    )

    rule.is_active = not rule.is_active
    rule.updated_at = timezone.now()

    rule.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    if rule.is_active:

        messages.success(
            request,
            "Access rule activated.",
        )

    else:

        messages.warning(
            request,
            "Access rule deactivated.",
        )

    return redirect(
        "access_control:access_rules"
    )


@login_required
def access_rule_delete(
    request,
    rule_id,
):
    """
    Delete an access rule.
    """

    rule = get_object_or_404(
        AccessRule,
        id=rule_id,
    )

    if request.method == "POST":

        rule.delete()

        messages.success(
            request,
            "Access rule deleted successfully.",
        )

        return redirect(
            "access_control:access_rules"
        )

    return render(
        request,
        "access_control/confirm_delete.html",
        {
            "rule": rule,
        },
    )


# ============================================================
# DOOR PERMISSIONS
# ============================================================

@login_required
def permission_list(request):
    """
    Display all door permissions.
    """

    permissions = (
        DoorPermission.objects
        .select_related(
            "door",
            "employee",
            "access_rule",
        )
        .order_by("-id")
    )

    roles = Role.objects.filter(
        is_active=True
    ).order_by("name")

    permission_roles = {
        role.id: role
        for role in roles
    }

    active_permissions = permissions.filter(
        is_active=True
    ).count()

    inactive_permissions = permissions.filter(
        is_active=False
    ).count()

    employee_permissions = permissions.filter(
        employee__isnull=False
    ).count()

    role_permissions = permissions.filter(
        role_id__isnull=False
    ).count()

    context = {
        "permissions": permissions,
        "permission_roles": permission_roles,
        "total_permissions": permissions.count(),
        "active_permissions": active_permissions,
        "inactive_permissions": inactive_permissions,
        "employee_permissions": employee_permissions,
        "role_permissions": role_permissions,
    }

    return render(
        request,
        "access_control/permissions.html",
        context,
    )


@login_required
def permission_add(request):
    """
    Create a new door permission.
    """

    doors = Door.objects.filter(
        is_active=True
    ).order_by("name")

    employees = Employee.objects.filter(
        status__iexact="active"
    ).order_by(
        "employee_number"
    )

    roles = Role.objects.filter(
        is_active=True
    ).order_by("name")

    access_rules = AccessRule.objects.filter(
        is_active=True
    ).order_by(
        "priority",
        "name",
    )

    if request.method == "POST":

        door_id = request.POST.get(
            "door_id"
        )

        employee_id = request.POST.get(
            "employee_id"
        )

        role_id = request.POST.get(
            "role_id"
        )

        access_rule_id = request.POST.get(
            "access_rule_id"
        )

        is_active = (
            request.POST.get("is_active")
            == "on"
        )

        # --------------------------------------------------------
        # DOOR
        # --------------------------------------------------------

        if not door_id:

            messages.error(
                request,
                "Please select a door.",
            )

            return render(
                request,
                "access_control/permission_form.html",
                {
                    "doors": doors,
                    "employees": employees,
                    "roles": roles,
                    "access_rules": access_rules,
                },
            )

        door = get_object_or_404(
            Door,
            id=door_id,
            is_active=True,
        )

        # --------------------------------------------------------
        # EMPLOYEE / ROLE
        # --------------------------------------------------------

        if not employee_id and not role_id:

            messages.error(
                request,
                "Please select either an employee or a role.",
            )

            return render(
                request,
                "access_control/permission_form.html",
                {
                    "doors": doors,
                    "employees": employees,
                    "roles": roles,
                    "access_rules": access_rules,
                },
            )

        # --------------------------------------------------------
        # EMPLOYEE
        # --------------------------------------------------------

        employee = None

        if employee_id:

            employee = get_object_or_404(
                Employee,
                id=employee_id,
                status__iexact="active",
            )

        # --------------------------------------------------------
        # ROLE
        # --------------------------------------------------------

        selected_role_id = None

        if role_id:

            role = get_object_or_404(
                Role,
                id=role_id,
                is_active=True,
            )

            selected_role_id = role.id

        # --------------------------------------------------------
        # ACCESS RULE
        # --------------------------------------------------------

        access_rule = None

        if access_rule_id:

            access_rule = get_object_or_404(
                AccessRule,
                id=access_rule_id,
                is_active=True,
            )

        # --------------------------------------------------------
        # CREATE
        # --------------------------------------------------------

        DoorPermission.objects.create(
            door=door,
            employee=employee,
            role_id=selected_role_id,
            access_rule=access_rule,
            is_active=is_active,
            created_at=timezone.now(),
        )

        messages.success(
            request,
            "Door permission created successfully.",
        )

        return redirect(
            "access_control:permissions"
        )

    context = {
        "doors": doors,
        "employees": employees,
        "roles": roles,
        "access_rules": access_rules,
    }

    return render(
        request,
        "access_control/permission_form.html",
        context,
    )


@login_required
def permission_edit(
    request,
    permission_id,
):
    """
    Edit an existing door permission.
    """

    permission = get_object_or_404(
        DoorPermission,
        id=permission_id,
    )

    doors = Door.objects.filter(
        is_active=True
    ).order_by("name")

    employees = Employee.objects.filter(
        status__iexact="active"
    ).order_by(
        "employee_number"
    )

    roles = Role.objects.filter(
        is_active=True
    ).order_by("name")

    access_rules = AccessRule.objects.filter(
        is_active=True
    ).order_by(
        "priority",
        "name",
    )

    if request.method == "POST":

        door_id = request.POST.get(
            "door_id"
        )

        employee_id = request.POST.get(
            "employee_id"
        )

        role_id = request.POST.get(
            "role_id"
        )

        access_rule_id = request.POST.get(
            "access_rule_id"
        )

        is_active = (
            request.POST.get("is_active")
            == "on"
        )

        if not door_id:

            messages.error(
                request,
                "Please select a door.",
            )

        elif not employee_id and not role_id:

            messages.error(
                request,
                "Please select either an employee or a role.",
            )

        else:

            permission.door = get_object_or_404(
                Door,
                id=door_id,
                is_active=True,
            )

            permission.employee = (
                get_object_or_404(
                    Employee,
                    id=employee_id,
                    status__iexact="active",
                )
                if employee_id
                else None
            )

            permission.role_id = (
                get_object_or_404(
                    Role,
                    id=role_id,
                    is_active=True,
                ).id
                if role_id
                else None
            )

            permission.access_rule = (
                get_object_or_404(
                    AccessRule,
                    id=access_rule_id,
                    is_active=True,
                )
                if access_rule_id
                else None
            )

            permission.is_active = is_active

            permission.save(
                update_fields=[
                    "door",
                    "employee",
                    "role_id",
                    "access_rule",
                    "is_active",
                ]
            )

            messages.success(
                request,
                "Door permission updated successfully.",
            )

            return redirect(
                "access_control:permissions"
            )

    context = {
        "permission": permission,
        "doors": doors,
        "employees": employees,
        "roles": roles,
        "access_rules": access_rules,
        "edit_mode": True,
    }

    return render(
        request,
        "access_control/permission_form.html",
        context,
    )


@login_required
def permission_toggle_status(
    request,
    permission_id,
):
    """
    Activate/deactivate a permission.
    """

    permission = get_object_or_404(
        DoorPermission,
        id=permission_id,
    )

    permission.is_active = not permission.is_active

    permission.save(
        update_fields=[
            "is_active",
        ]
    )

    if permission.is_active:

        messages.success(
            request,
            "Permission activated.",
        )

    else:

        messages.warning(
            request,
            "Permission deactivated.",
        )

    return redirect(
        "access_control:permissions"
    )


@login_required
def permission_delete(
    request,
    permission_id,
):
    """
    Delete a permission.
    """

    permission = get_object_or_404(
        DoorPermission,
        id=permission_id,
    )

    if request.method == "POST":

        permission.delete()

        messages.success(
            request,
            "Door permission deleted successfully.",
        )

        return redirect(
            "access_control:permissions"
        )

    return render(
        request,
        "access_control/permission_confirm_delete.html",
        {
            "permission": permission,
        },
    )



# ============================================================
# DOORS
# ============================================================

@login_required
def doors(request):
    """
    Display all access-control doors.
    """

    door_list = Door.objects.all().order_by("name")

    total_doors = door_list.count()

    active_doors = door_list.filter(
        is_active=True
    ).count()

    inactive_doors = door_list.filter(
        is_active=False
    ).count()

    context = {
        "doors": door_list,
        "door_list": door_list,

        "total_doors": total_doors,
        "active_doors": active_doors,
        "inactive_doors": inactive_doors,
    }

    return render(
        request,
        "dashboard/doors.html",
        context,
    )
# ============================================================
# DOOR CRUD
# ============================================================

@login_required
def door_add(request):
    """
    Add a new access-control door.
    """

    if request.method == "POST":

        door_code = request.POST.get(
            "door_code",
            "",
        ).strip()

        name = request.POST.get(
            "name",
            "",
        ).strip()

        location = request.POST.get(
            "location",
            "",
        ).strip()

        lock_type = request.POST.get(
            "lock_type",
            "",
        ).strip()

        unlock_duration_seconds = request.POST.get(
            "unlock_duration_seconds",
            "5",
        ).strip()

        sensor_enabled = (
            request.POST.get("sensor_enabled")
            == "on"
        )

        exit_button_enabled = (
            request.POST.get("exit_button_enabled")
            == "on"
        )

        is_active = (
            request.POST.get("is_active")
            == "on"
        )

        # --------------------------------------------------------
        # VALIDATE DOOR CODE
        # --------------------------------------------------------

        if not door_code:

            messages.error(
                request,
                "Door code is required.",
            )

            return render(
                request,
                "access_control/door_form.html",
                {
                    "door": None,
                    "edit_mode": False,
                },
            )

        # --------------------------------------------------------
        # VALIDATE NAME
        # --------------------------------------------------------

        if not name:

            messages.error(
                request,
                "Door name is required.",
            )

            return render(
                request,
                "access_control/door_form.html",
                {
                    "door": None,
                    "edit_mode": False,
                },
            )

        # --------------------------------------------------------
        # VALIDATE UNLOCK DURATION
        # --------------------------------------------------------

        try:

            unlock_duration_seconds = int(
                unlock_duration_seconds
            )

            if unlock_duration_seconds <= 0:

                raise ValueError

        except (TypeError, ValueError):

            messages.error(
                request,
                "Unlock duration must be a positive number.",
            )

            return render(
                request,
                "access_control/door_form.html",
                {
                    "door": None,
                    "edit_mode": False,
                },
            )

        # --------------------------------------------------------
        # CHECK DUPLICATE DOOR CODE
        # --------------------------------------------------------

        if Door.objects.filter(
            door_code=door_code
        ).exists():

            messages.error(
                request,
                "A door with this door code already exists.",
            )

            return render(
                request,
                "access_control/door_form.html",
                {
                    "door": None,
                    "edit_mode": False,
                },
            )

        # --------------------------------------------------------
        # CREATE DOOR
        # --------------------------------------------------------

        try:

            Door.objects.create(
                door_code=door_code,
                name=name,
                location=location or None,
                lock_type=lock_type or None,
                unlock_duration_seconds=unlock_duration_seconds,
                sensor_enabled=sensor_enabled,
                exit_button_enabled=exit_button_enabled,
                is_active=is_active,
            )

            messages.success(
                request,
                f"Door '{name}' was added successfully.",
            )

            return redirect(
                "access_control:doors"
            )

        except Exception as exc:

            messages.error(
                request,
                f"Unable to add door: {exc}",
            )

    return render(
        request,
        "access_control/door_form.html",
        {
            "door": None,
            "edit_mode": False,
        },
    )


@login_required
def door_detail(request, door_id):
    """
    Display details of a single door.
    """

    door = get_object_or_404(
        Door,
        id=door_id,
    )

    return render(
        request,
        "access_control/door_detail.html",
        {
            "door": door,
        },
    )


@login_required
def door_edit(request, door_id):
    """
    Edit an existing access-control door.
    """

    door = get_object_or_404(
        Door,
        id=door_id,
    )

    if request.method == "POST":

        door_code = request.POST.get(
            "door_code",
            "",
        ).strip()

        name = request.POST.get(
            "name",
            "",
        ).strip()

        location = request.POST.get(
            "location",
            "",
        ).strip()

        lock_type = request.POST.get(
            "lock_type",
            "",
        ).strip()

        unlock_duration_seconds = request.POST.get(
            "unlock_duration_seconds",
            "5",
        ).strip()

        sensor_enabled = (
            request.POST.get("sensor_enabled")
            == "on"
        )

        exit_button_enabled = (
            request.POST.get("exit_button_enabled")
            == "on"
        )

        is_active = (
            request.POST.get("is_active")
            == "on"
        )

        # --------------------------------------------------------
        # VALIDATE DOOR CODE
        # --------------------------------------------------------

        if not door_code:

            messages.error(
                request,
                "Door code is required.",
            )

            return render(
                request,
                "access_control/door_form.html",
                {
                    "door": door,
                    "edit_mode": True,
                },
            )

        # --------------------------------------------------------
        # VALIDATE NAME
        # --------------------------------------------------------

        if not name:

            messages.error(
                request,
                "Door name is required.",
            )

            return render(
                request,
                "access_control/door_form.html",
                {
                    "door": door,
                    "edit_mode": True,
                },
            )

        # --------------------------------------------------------
        # VALIDATE UNLOCK DURATION
        # --------------------------------------------------------

        try:

            unlock_duration_seconds = int(
                unlock_duration_seconds
            )

            if unlock_duration_seconds <= 0:

                raise ValueError

        except (TypeError, ValueError):

            messages.error(
                request,
                "Unlock duration must be a positive number.",
            )

            return render(
                request,
                "access_control/door_form.html",
                {
                    "door": door,
                    "edit_mode": True,
                },
            )

        # --------------------------------------------------------
        # CHECK DUPLICATE DOOR CODE
        # --------------------------------------------------------

        duplicate_code = Door.objects.filter(
            door_code=door_code
        ).exclude(
            id=door.id
        ).exists()

        if duplicate_code:

            messages.error(
                request,
                "Another door already uses this door code.",
            )

            return render(
                request,
                "access_control/door_form.html",
                {
                    "door": door,
                    "edit_mode": True,
                },
            )

        # --------------------------------------------------------
        # UPDATE
        # --------------------------------------------------------

        try:

            door.door_code = door_code
            door.name = name
            door.location = location or None
            door.lock_type = lock_type or None
            door.unlock_duration_seconds = (
                unlock_duration_seconds
            )
            door.sensor_enabled = sensor_enabled
            door.exit_button_enabled = (
                exit_button_enabled
            )
            door.is_active = is_active

            if hasattr(door, "updated_at"):

                door.updated_at = timezone.now()

                door.save(
                    update_fields=[
                        "door_code",
                        "name",
                        "location",
                        "lock_type",
                        "unlock_duration_seconds",
                        "sensor_enabled",
                        "exit_button_enabled",
                        "is_active",
                        "updated_at",
                    ]
                )

            else:

                door.save()

            messages.success(
                request,
                f"Door '{door.name}' was updated successfully.",
            )

            return redirect(
                "access_control:doors"
            )

        except Exception as exc:

            messages.error(
                request,
                f"Unable to update door: {exc}",
            )

    return render(
        request,
        "access_control/door_form.html",
        {
            "door": door,
            "edit_mode": True,
        },
    )


@login_required
def door_toggle_status(request, door_id):
    """
    Activate or deactivate a door.
    """

    door = get_object_or_404(
        Door,
        id=door_id,
    )

    door.is_active = not door.is_active

    if hasattr(door, "updated_at"):

        door.updated_at = timezone.now()

        door.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

    else:

        door.save(
            update_fields=[
                "is_active",
            ]
        )

    if door.is_active:

        messages.success(
            request,
            f"Door '{door.name}' has been activated.",
        )

    else:

        messages.warning(
            request,
            f"Door '{door.name}' has been deactivated.",
        )

    return redirect(
        "access_control:doors"
    )


@login_required
def door_delete(request, door_id):
    """
    Delete an existing door.
    """

    door = get_object_or_404(
        Door,
        id=door_id,
    )

    if request.method == "POST":

        door_name = door.name

        try:

            door.delete()

            messages.success(
                request,
                f"Door '{door_name}' was deleted successfully.",
            )

            return redirect(
                "access_control:doors"
            )

        except Exception as exc:

            messages.error(
                request,
                f"Unable to delete door: {exc}",
            )

            return redirect(
                "access_control:doors"
            )

    return render(
        request,
        "access_control/door_confirm_delete.html",
        {
            "door": door,
        },
    )

# ============================================================
# ROLES
# ============================================================

@login_required
def role_list(request):
    """
    Display all roles.
    """

    roles = Role.objects.all().order_by("name")

    total_roles = roles.count()

    active_roles = roles.filter(
        is_active=True
    ).count()

    inactive_roles = roles.filter(
        is_active=False
    ).count()

    context = {
        "roles": roles,
        "total_roles": total_roles,
        "active_roles": active_roles,
        "inactive_roles": inactive_roles,
    }

    return render(
        request,
        "access_control/roles.html",
        context,
    )


@login_required
def role_add(request):
    """
    Add a new role.
    """

    if request.method == "POST":

        name = request.POST.get(
            "name",
            "",
        ).strip()

        description = request.POST.get(
            "description",
            "",
        ).strip()

        is_active = (
            request.POST.get("is_active")
            == "on"
        )

        # --------------------------------------------------------
        # VALIDATE NAME
        # --------------------------------------------------------

        if not name:

            messages.error(
                request,
                "Role name is required.",
            )

            return render(
                request,
                "access_control/role_form.html",
                {
                    "role": None,
                    "edit_mode": False,
                },
            )

        # --------------------------------------------------------
        # CHECK DUPLICATE ROLE
        # --------------------------------------------------------

        if Role.objects.filter(
            name__iexact=name
        ).exists():

            messages.error(
                request,
                "A role with this name already exists.",
            )

            return render(
                request,
                "access_control/role_form.html",
                {
                    "role": None,
                    "edit_mode": False,
                },
            )

        # --------------------------------------------------------
        # CREATE ROLE
        # --------------------------------------------------------

        try:

            Role.objects.create(
                name=name,
                description=description or None,
                is_active=is_active,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )

            messages.success(
                request,
                f"Role '{name}' was added successfully.",
            )

            return redirect(
                "access_control:roles"
            )

        except Exception as exc:

            messages.error(
                request,
                f"Unable to add role: {exc}",
            )

    return render(
        request,
        "access_control/role_form.html",
        {
            "role": None,
            "edit_mode": False,
        },
    )


@login_required
def role_detail(request, role_id):
    """
    Display details of a single role.
    """

    role = get_object_or_404(
        Role,
        id=role_id,
    )

    return render(
        request,
        "access_control/role_detail.html",
        {
            "role": role,
        },
    )


@login_required
def role_edit(request, role_id):
    """
    Edit an existing role.
    """

    role = get_object_or_404(
        Role,
        id=role_id,
    )

    if request.method == "POST":

        name = request.POST.get(
            "name",
            "",
        ).strip()

        description = request.POST.get(
            "description",
            "",
        ).strip()

        is_active = (
            request.POST.get("is_active")
            == "on"
        )

        # --------------------------------------------------------
        # VALIDATE NAME
        # --------------------------------------------------------

        if not name:

            messages.error(
                request,
                "Role name is required.",
            )

            return render(
                request,
                "access_control/role_form.html",
                {
                    "role": role,
                    "edit_mode": True,
                },
            )

        # --------------------------------------------------------
        # CHECK DUPLICATE ROLE
        # --------------------------------------------------------

        duplicate_role = (
            Role.objects
            .filter(
                name__iexact=name
            )
            .exclude(
                id=role.id
            )
            .exists()
        )

        if duplicate_role:

            messages.error(
                request,
                "Another role with this name already exists.",
            )

            return render(
                request,
                "access_control/role_form.html",
                {
                    "role": role,
                    "edit_mode": True,
                },
            )

        # --------------------------------------------------------
        # UPDATE ROLE
        # --------------------------------------------------------

        try:

            role.name = name
            role.description = (
                description or None
            )
            role.is_active = is_active
            role.updated_at = timezone.now()

            role.save(
                update_fields=[
                    "name",
                    "description",
                    "is_active",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                f"Role '{role.name}' was updated successfully.",
            )

            return redirect(
                "access_control:role_detail",
                role_id=role.id,
            )

        except Exception as exc:

            messages.error(
                request,
                f"Unable to update role: {exc}",
            )

    return render(
        request,
        "access_control/role_form.html",
        {
            "role": role,
            "edit_mode": True,
        },
    )


@login_required
def role_toggle_status(request, role_id):
    """
    Activate or deactivate a role.
    """

    role = get_object_or_404(
        Role,
        id=role_id,
    )

    role.is_active = not role.is_active
    role.updated_at = timezone.now()

    role.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    if role.is_active:

        messages.success(
            request,
            f"Role '{role.name}' has been activated.",
        )

    else:

        messages.warning(
            request,
            f"Role '{role.name}' has been deactivated.",
        )

    return redirect(
        "access_control:roles"
    )


@login_required
def role_delete(request, role_id):
    """
    Delete an existing role.
    """

    role = get_object_or_404(
        Role,
        id=role_id,
    )

    if request.method == "POST":

        role_name = role.name

        try:

            role.delete()

            messages.success(
                request,
                f"Role '{role_name}' was deleted successfully.",
            )

            return redirect(
                "access_control:roles"
            )

        except Exception as exc:

            messages.error(
                request,
                f"Unable to delete role: {exc}",
            )

            return redirect(
                "access_control:roles"
            )

    return render(
        request,
        "access_control/role_confirm_delete.html",
        {
            "role": role,
        },
    )


# ============================================================
# ACCESS LOGS
# ============================================================

@login_required
def access_log_list(request):
    """
    Display access-control logs.
    """

    logs = (
        AccessLog.objects
        .select_related(
            "employee",
            "door",
            "rfid_card",
        )
        .order_by("-event_time")
    )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search = request.GET.get(
        "search",
        "",
    ).strip()

    if search:

        logs = logs.filter(
            models.Q(
                employee__employee_number__icontains=search
            )
            | models.Q(
                employee__first_name__icontains=search
            )
            | models.Q(
                employee__last_name__icontains=search
            )
            | models.Q(
                door__name__icontains=search
            )
            | models.Q(
                authentication_method__icontains=search
            )
            | models.Q(
                action__icontains=search
            )
            | models.Q(
                reason__icontains=search
            )
        )

    # --------------------------------------------------------
    # FILTER BY ACTION
    # --------------------------------------------------------

    action = request.GET.get(
        "action",
        "",
    ).strip().lower()

    if action:

        logs = logs.filter(
            action__iexact=action
        )

    # --------------------------------------------------------
    # FILTER BY AUTHENTICATION METHOD
    # --------------------------------------------------------

    authentication_method = request.GET.get(
        "authentication_method",
        "",
    ).strip()

    if authentication_method:

        logs = logs.filter(
            authentication_method__iexact=
            authentication_method
        )

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    total_logs = AccessLog.objects.count()

    granted_logs = AccessLog.objects.filter(
        action__iexact="granted"
    ).count()

    denied_logs = AccessLog.objects.filter(
        action__iexact="denied"
    ).count()

    today = timezone.localdate()

    today_logs = AccessLog.objects.filter(
        event_time__date=today
    ).count()

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {
        "logs": logs,

        "total_logs": total_logs,
        "granted_logs": granted_logs,
        "denied_logs": denied_logs,
        "today_logs": today_logs,

        "search": search,
        "selected_action": action,
        "selected_authentication_method":
            authentication_method,
    }

    return render(
        request,
        "access_control/access_logs.html",
        context,
    )



@login_required
def access_log_detail(request, log_id):

    log = get_object_or_404(
        AccessLog.objects.select_related(
            "employee",
            "door",
            "rfid_card",
        ),
        pk=log_id,
    )

    return render(
        request,
        "access_control/access_log_detail.html",
        {
            "log": log,
        },
    )


@login_required
def export_access_logs_csv(request):
    """
    Export access logs matching the current search and filters.
    """

    logs = AccessLog.objects.select_related(
        "employee",
        "door",
        "rfid_card",
    ).order_by("-event_time")

    # Search
    search = request.GET.get("search", "").strip()

    if search:
        from django.db.models import Q

        logs = logs.filter(
            Q(employee__employee_number__icontains=search)
            | Q(employee__first_name__icontains=search)
            | Q(employee__last_name__icontains=search)
            | Q(door__name__icontains=search)
            | Q(authentication_method__icontains=search)
            | Q(action__icontains=search)
            | Q(reason__icontains=search)
        )

    # Authentication method
    authentication_method = request.GET.get(
        "authentication_method", ""
    ).strip()

    if authentication_method:
        logs = logs.filter(
            authentication_method__iexact=authentication_method
        )

    # Result/action
    action = request.GET.get("action", "").strip()

    if action:
        logs = logs.filter(action__iexact=action)

    # CSV response
    response = HttpResponse(
        content_type="text/csv; charset=utf-8"
    )
    response["Content-Disposition"] = (
        'attachment; filename="access_logs.csv"'
    )

    # Excel-friendly UTF-8 BOM
    response.write("\ufeff")

    writer = csv.writer(response)

    writer.writerow([
        "Log ID",
        "Employee Name",
        "Employee Number",
        "Employee ID",
        "Door Name",
        "Door Code",
        "Authentication Method",
        "Result",
        "Confidence (%)",
        "Reason",
        "IP Address",
        "Event Date & Time",
        "Created At",
    ])

    for log in logs.iterator(chunk_size=500):

        employee = log.employee
        door = log.door

        employee_name = (
            f"{employee.first_name} {employee.last_name}".strip()
            if employee else "Unknown Employee"
        )

        writer.writerow([
            log.id,
            employee_name,
            employee.employee_number if employee else "",
            employee.employee_id if employee else "",
            door.name if door else "Unknown Door",
            door.door_code if door else "",
            log.authentication_method or "",
            log.action,
            log.confidence_score
            if log.confidence_score is not None else "",
            log.reason or "",
            log.ip_address or "",
            log.event_time.strftime("%Y-%m-%d %H:%M:%S")
            if log.event_time else "",
            log.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if log.created_at else "",
        ])

    return response

def export_access_logs_pdf(request):
    """Export access logs as a PDF report."""

    # Import your existing access log model.
    from .models import AccessLog

    logs = AccessLog.objects.all().order_by("-id")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        'attachment; filename="access_logs.pdf"'
    )

    document = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()
    elements = [
        Paragraph("Smart Access Control System - Access Logs", styles["Title"]),
        Spacer(1, 8 * mm),
    ]

    data = [[
        "Log ID",
        "Employee",
        "Door",
        "Authentication",
        "Result",
        "Date/Time",
    ]]

    for log in logs:
        data.append([
            str(getattr(log, "id", "")),
            str(getattr(log, "employee", "") or "-"),
            str(getattr(log, "door", "") or "-"),
            str(
                getattr(log, "authentication_method", "")
                or getattr(log, "auth_method", "")
                or "-"
            ),
            str(
                getattr(log, "status", "")
                or getattr(log, "access_result", "")
                or "-"
            ),
            str(
                getattr(log, "timestamp", "")
                or getattr(log, "access_time", "")
                or getattr(log, "created_at", "")
                or "-"
            ),
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#263746")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F2F5F7"),
        ]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))

    elements.append(table)
    document.build(elements)

    return response

@csrf_exempt
def fingerprint_authenticate(request):
    """
    Authenticate an R307 fingerprint and determine
    whether the employee is allowed to access a door.

    Expected POST JSON:

    {
        "fingerprint_id": 1,
        "confidence": 65,
        "door_code": "DR-001"
    }
    """

    # ============================================================
    # ONLY POST
    # ============================================================

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "authenticated": False,
                "access_granted": False,
                "message": "Only POST requests are allowed.",
            },
            status=405,
        )

    # ============================================================
    # READ JSON
    # ============================================================

    try:

        data = json.loads(request.body)

    except (json.JSONDecodeError, TypeError):

        return JsonResponse(
            {
                "success": False,
                "authenticated": False,
                "access_granted": False,
                "message": "Invalid JSON.",
            },
            status=400,
        )

    # ============================================================
    # FINGERPRINT ID
    # ============================================================

    fingerprint_id = data.get("fingerprint_id")

    if fingerprint_id is None:

        return JsonResponse(
            {
                "success": False,
                "authenticated": False,
                "access_granted": False,
                "message": "fingerprint_id is required.",
            },
            status=400,
        )

    try:

        fingerprint_id = int(fingerprint_id)

    except (TypeError, ValueError):

        return JsonResponse(
            {
                "success": False,
                "authenticated": False,
                "access_granted": False,
                "message": "fingerprint_id must be an integer.",
            },
            status=400,
        )

    # ============================================================
    # CONFIDENCE
    # ============================================================

    confidence = data.get("confidence")

    try:

        confidence = (
            float(confidence)
            if confidence is not None
            else None
        )

    except (TypeError, ValueError):

        confidence = None

    # ============================================================
    # DOOR CODE
    # ============================================================

    door_code = data.get(
        "door_code"
    )

    if not door_code:

        return JsonResponse(
            {
                "success": False,
                "authenticated": False,
                "access_granted": False,
                "message": "door_code is required.",
            },
            status=400,
        )

    door_code = str(
        door_code
    ).strip()

    # ============================================================
    # FIND FINGERPRINT
    # ============================================================

    try:

        fingerprint = (
            Fingerprint.objects
            .select_related("employee")
            .get(
                fingerprint_index=fingerprint_id,
                sensor_type__iexact="R307",
                status__iexact="active",
            )
        )

    except Fingerprint.DoesNotExist:

        return JsonResponse(
            {
                "success": True,
                "authenticated": False,
                "access_granted": False,
                "message": "Fingerprint is not registered.",
                "fingerprint_id": fingerprint_id,
                "door_code": door_code,
            },
            status=200,
        )

    # ============================================================
    # EMPLOYEE
    # ============================================================

    employee = fingerprint.employee

    if employee is None:

        return JsonResponse(
            {
                "success": True,
                "authenticated": False,
                "access_granted": False,
                "message": "Fingerprint is not assigned to an employee.",
                "fingerprint_id": fingerprint_id,
                "door_code": door_code,
            },
            status=200,
        )

    # ============================================================
    # EMPLOYEE STATUS
    # ============================================================

    if (
        not employee.status
        or employee.status.lower() != "active"
    ):

        return JsonResponse(
            {
                "success": True,
                "authenticated": True,
                "access_granted": False,
                "message": "Employee account is not active.",
                "employee": {
                    "id": employee.employee_id,
                    "employee_number": employee.employee_number,
                },
                "door_code": door_code,
            },
            status=200,
        )

    # ============================================================
    # FIND DOOR
    # ============================================================

    try:

        door = Door.objects.get(
            door_code=door_code
        )

    except Door.DoesNotExist:

        return JsonResponse(
            {
                "success": True,
                "authenticated": True,
                "access_granted": False,
                "message": "Door not found.",
                "employee": {
                    "id": employee.employee_id,
                    "employee_number": employee.employee_number,
                },
                "door_code": door_code,
            },
            status=200,
        )

    # ============================================================
    # DOOR STATUS
    # ============================================================

    if not door.is_active:

        AccessLog.objects.create(
            employee=employee,
            door=door,
            authentication_method="Fingerprint",
            action="denied",
            reason="Door is inactive.",
            confidence_score=confidence,
            event_time=timezone.now(),
            created_at=timezone.now(),
        )

        return JsonResponse(
            {
                "success": True,
                "authenticated": True,
                "access_granted": False,
                "message": "Door is inactive.",
                "employee": {
                    "id": employee.employee_id,
                    "employee_number": employee.employee_number,
                    "name": (
                        f"{employee.first_name} "
                        f"{employee.middle_name or ''} "
                        f"{employee.last_name}"
                    ).replace("  ", " ").strip(),
                },
                "door": {
                    "id": door.id,
                    "door_code": door.door_code,
                    "name": door.name,
                },
            },
            status=200,
        )

    # ============================================================
    # FIND EMPLOYEE DOOR PERMISSION
    # ============================================================

    permission = (
        DoorPermission.objects
        .select_related("access_rule")
        .filter(
            door=door,
            employee=employee,
            is_active=True,
        )
        .order_by(
            "-id"
        )
        .first()
    )

    if permission is None:

        AccessLog.objects.create(
            employee=employee,
            door=door,
            authentication_method="Fingerprint",
            action="denied",
            reason="No active door permission.",
            confidence_score=confidence,
            event_time=timezone.now(),
            created_at=timezone.now(),
        )

        return JsonResponse(
            {
                "success": True,
                "authenticated": True,
                "access_granted": False,
                "message": "Access denied. No active door permission.",
                "employee": {
                    "id": employee.employee_id,
                    "employee_number": employee.employee_number,
                    "name": (
                        f"{employee.first_name} "
                        f"{employee.middle_name or ''} "
                        f"{employee.last_name}"
                    ).replace("  ", " ").strip(),
                },
                "door": {
                    "id": door.id,
                    "door_code": door.door_code,
                    "name": door.name,
                },
            },
            status=200,
        )

    # ============================================================
    # ACCESS RULE
    # ============================================================

    access_rule = permission.access_rule

    if access_rule is None:

        AccessLog.objects.create(
            employee=employee,
            door=door,
            authentication_method="Fingerprint",
            action="denied",
            reason="No access rule assigned.",
            confidence_score=confidence,
            event_time=timezone.now(),
            created_at=timezone.now(),
        )

        return JsonResponse(
            {
                "success": True,
                "authenticated": True,
                "access_granted": False,
                "message": "Access denied. No access rule assigned.",
                "employee": {
                    "id": employee.employee_id,
                    "employee_number": employee.employee_number,
                },
                "door": {
                    "id": door.id,
                    "door_code": door.door_code,
                    "name": door.name,
                },
            },
            status=200,
        )

    # ============================================================
    # ACCESS RULE ACTIVE?
    # ============================================================

    if not access_rule.is_active:

        AccessLog.objects.create(
            employee=employee,
            door=door,
            authentication_method="Fingerprint",
            action="denied",
            reason="Access rule is inactive.",
            confidence_score=confidence,
            event_time=timezone.now(),
            created_at=timezone.now(),
        )

        return JsonResponse(
            {
                "success": True,
                "authenticated": True,
                "access_granted": False,
                "message": "Access denied. Access rule is inactive.",
                "employee": {
                    "id": employee.employee_id,
                    "employee_number": employee.employee_number,
                },
                "door": {
                    "id": door.id,
                    "door_code": door.door_code,
                    "name": door.name,
                },
            },
            status=200,
        )

    # ============================================================
    # CURRENT DATE/TIME
    # ============================================================

    now = timezone.localtime()

    current_date = now.date()
    current_time = now.time()
    weekday = now.weekday()

    # ============================================================
    # VALID DATE RANGE
    # ============================================================

    if (
        access_rule.valid_from
        and current_date < access_rule.valid_from
    ):

        AccessLog.objects.create(
            employee=employee,
            door=door,
            authentication_method="Fingerprint",
            action="denied",
            reason="Access rule is not yet valid.",
            confidence_score=confidence,
            event_time=timezone.now(),
            created_at=timezone.now(),
        )

        return JsonResponse(
            {
                "success": True,
                "authenticated": True,
                "access_granted": False,
                "message": "Access denied. Rule is not yet valid.",
            },
            status=200,
        )

    if (
        access_rule.valid_until
        and current_date > access_rule.valid_until
    ):

        AccessLog.objects.create(
            employee=employee,
            door=door,
            authentication_method="Fingerprint",
            action="denied",
            reason="Access rule has expired.",
            confidence_score=confidence,
            event_time=timezone.now(),
            created_at=timezone.now(),
        )

        return JsonResponse(
            {
                "success": True,
                "authenticated": True,
                "access_granted": False,
                "message": "Access denied. Rule has expired.",
            },
            status=200,
        )

    # ============================================================
    # DAY CHECK
    # ============================================================

    allowed_days = {
        0: access_rule.monday,
        1: access_rule.tuesday,
        2: access_rule.wednesday,
        3: access_rule.thursday,
        4: access_rule.friday,
        5: access_rule.saturday,
        6: access_rule.sunday,
    }

    if not allowed_days.get(
        weekday,
        False,
    ):

        AccessLog.objects.create(
            employee=employee,
            door=door,
            authentication_method="Fingerprint",
            action="denied",
            reason="Access is not allowed on this day.",
            confidence_score=confidence,
            event_time=timezone.now(),
            created_at=timezone.now(),
        )

        return JsonResponse(
            {
                "success": True,
                "authenticated": True,
                "access_granted": False,
                "message": "Access denied on this day.",
            },
            status=200,
        )

    # ============================================================
    # TIME CHECK
    # ============================================================

    start_time = access_rule.start_time
    end_time = access_rule.end_time

    if start_time and end_time:

        # Normal time range
        if start_time <= end_time:

            time_allowed = (
                start_time
                <= current_time
                <= end_time
            )

        # Overnight time range
        else:

            time_allowed = (
                current_time >= start_time
                or current_time <= end_time
            )

        if not time_allowed:

            AccessLog.objects.create(
                employee=employee,
                door=door,
                authentication_method="Fingerprint",
                action="denied",
                reason="Access is outside the permitted time.",
                confidence_score=confidence,
                event_time=timezone.now(),
                created_at=timezone.now(),
            )

            return JsonResponse(
                {
                    "success": True,
                    "authenticated": True,
                    "access_granted": False,
                    "message": "Access denied outside permitted time.",
                },
                status=200,
            )

    # ============================================================
    # ACCESS TYPE
    # ============================================================

    if (
        access_rule.access_type
        and access_rule.access_type.lower() == "deny"
    ):

        AccessLog.objects.create(
            employee=employee,
            door=door,
            authentication_method="Fingerprint",
            action="denied",
            reason="Access rule explicitly denies access.",
            confidence_score=confidence,
            event_time=timezone.now(),
            created_at=timezone.now(),
        )

        return JsonResponse(
            {
                "success": True,
                "authenticated": True,
                "access_granted": False,
                "message": "Access denied by access rule.",
                "employee": {
                    "id": employee.employee_id,
                    "employee_number": employee.employee_number,
                    "name": (
                        f"{employee.first_name} "
                        f"{employee.middle_name or ''} "
                        f"{employee.last_name}"
                    ).replace("  ", " ").strip(),
                },
                "door": {
                    "id": door.id,
                    "door_code": door.door_code,
                    "name": door.name,
                },
            },
            status=200,
        )

    # ============================================================
    # ACCESS GRANTED
    # ============================================================

    AccessLog.objects.create(
        employee=employee,
        door=door,
        authentication_method="Fingerprint",
        action="granted",
        reason="Fingerprint authenticated and access permission approved.",
        confidence_score=confidence,
        event_time=timezone.now(),
        created_at=timezone.now(),
    )

    return JsonResponse(
        {
            "success": True,
            "authenticated": True,
            "access_granted": True,
            "message": "Access granted.",
            "employee": {
                "id": employee.employee_id,
                "employee_number": employee.employee_number,
                "name": (
                    f"{employee.first_name} "
                    f"{employee.middle_name or ''} "
                    f"{employee.last_name}"
                ).replace("  ", " ").strip(),
            },
            "fingerprint": {
                "id": fingerprint.fingerprint_index,
                "sensor_type": fingerprint.sensor_type,
                "quality_score": fingerprint.quality_score,
            },
            "door": {
                "id": door.id,
                "door_code": door.door_code,
                "name": door.name,
                "unlock_duration_seconds": (
                    door.unlock_duration_seconds
                ),
            },
            "timestamp": timezone.now().isoformat(),
        },
        status=200,
    )


@login_required
def security_audit_report(request):
    """Display a security audit report using existing access logs."""

    # Reuse the model already used by your access log page.
    from .models import AccessLog

    logs = AccessLog.objects.all().order_by("-id")

    context = {
        "logs": logs,
        "total_logs": logs.count(),
    }

    return render(
        request,
        "access_control/security_audit_report.html",
        context,
    ) 