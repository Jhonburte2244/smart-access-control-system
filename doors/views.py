from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Door


@login_required
def door_list(request):
    """
    Display all doors with search and status filtering.
    """

    search = request.GET.get("search", "").strip()
    selected_status = request.GET.get("status", "").strip()

    doors = Door.objects.all().order_by("name")

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------
    if search:
        doors = doors.filter(
            Q(door_code__icontains=search)
            | Q(name__icontains=search)
            | Q(location__icontains=search)
            | Q(lock_type__icontains=search)
        )

    # ---------------------------------------------------------
    # STATUS FILTER
    # ---------------------------------------------------------
    if selected_status == "active":
        doors = doors.filter(is_active=True)

    elif selected_status == "inactive":
        doors = doors.filter(is_active=False)

    # ---------------------------------------------------------
    # COUNTS
    # ---------------------------------------------------------
    total_doors = Door.objects.count()
    active_doors = Door.objects.filter(is_active=True).count()
    inactive_doors = Door.objects.filter(is_active=False).count()

    context = {
        "doors": doors,
        "total_doors": total_doors,
        "active_doors": active_doors,
        "inactive_doors": inactive_doors,
        "search": search,
        "selected_status": selected_status,
    }

    return render(
        request,
        "doors/list.html",
        context,
    )


@login_required
def door_add(request):
    """
    Add a new door.
    """

    if request.method == "POST":

        door_code = request.POST.get("door_code", "").strip()
        name = request.POST.get("name", "").strip()
        location = request.POST.get("location", "").strip()
        lock_type = request.POST.get("lock_type", "").strip()

        unlock_duration = request.POST.get(
            "unlock_duration_seconds",
            "5",
        ).strip()

        sensor_enabled = request.POST.get("sensor_enabled") == "on"
        exit_button_enabled = (
            request.POST.get("exit_button_enabled") == "on"
        )

        is_active = request.POST.get("is_active") == "on"

        # -----------------------------------------------------
        # REQUIRED FIELDS
        # -----------------------------------------------------
        if not door_code:
            messages.error(
                request,
                "Door code is required.",
            )

            return render(
                request,
                "doors/add.html",
                {
                    "door_code": door_code,
                    "name": name,
                    "location": location,
                    "lock_type": lock_type,
                    "unlock_duration_seconds": unlock_duration,
                    "sensor_enabled": sensor_enabled,
                    "exit_button_enabled": exit_button_enabled,
                    "is_active": is_active,
                },
            )

        if not name:
            messages.error(
                request,
                "Door name is required.",
            )

            return render(
                request,
                "doors/add.html",
                {
                    "door_code": door_code,
                    "name": name,
                    "location": location,
                    "lock_type": lock_type,
                    "unlock_duration_seconds": unlock_duration,
                    "sensor_enabled": sensor_enabled,
                    "exit_button_enabled": exit_button_enabled,
                    "is_active": is_active,
                },
            )

        # -----------------------------------------------------
        # DUPLICATE DOOR CODE
        # -----------------------------------------------------
        if Door.objects.filter(
            door_code__iexact=door_code
        ).exists():

            messages.error(
                request,
                "A door with this door code already exists.",
            )

            return render(
                request,
                "doors/add.html",
                {
                    "door_code": door_code,
                    "name": name,
                    "location": location,
                    "lock_type": lock_type,
                    "unlock_duration_seconds": unlock_duration,
                    "sensor_enabled": sensor_enabled,
                    "exit_button_enabled": exit_button_enabled,
                    "is_active": is_active,
                },
            )

        # -----------------------------------------------------
        # UNLOCK DURATION VALIDATION
        # -----------------------------------------------------
        try:
            unlock_duration = int(unlock_duration)

            if unlock_duration < 1:
                raise ValueError

        except (ValueError, TypeError):

            messages.error(
                request,
                "Unlock duration must be a positive number.",
            )

            return render(
                request,
                "doors/add.html",
                {
                    "door_code": door_code,
                    "name": name,
                    "location": location,
                    "lock_type": lock_type,
                    "unlock_duration_seconds": unlock_duration,
                    "sensor_enabled": sensor_enabled,
                    "exit_button_enabled": exit_button_enabled,
                    "is_active": is_active,
                },
            )

        # -----------------------------------------------------
        # CREATE DOOR
        # -----------------------------------------------------
        now = timezone.now()

        Door.objects.create(
            door_code=door_code,
            name=name,
            location=location or None,
            lock_type=lock_type or None,
            unlock_duration_seconds=unlock_duration,
            sensor_enabled=sensor_enabled,
            exit_button_enabled=exit_button_enabled,
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

        messages.success(
            request,
            f"Door '{name}' was added successfully.",
        )

        return redirect(
            "access_control:doors"
        )

    # ---------------------------------------------------------
    # GET REQUEST
    # ---------------------------------------------------------
    return render(
        request,
        "doors/add.html",
    )


@login_required
def door_detail(request, door_id):
    """
    Display details of one door.
    """

    door = get_object_or_404(
        Door,
        id=door_id,
    )

    return render(
        request,
        "doors/detail.html",
        {
            "door": door,
        },
    )


@login_required
def door_edit(request, door_id):
    """
    Edit an existing door.
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

        unlock_duration = request.POST.get(
            "unlock_duration_seconds",
            "5",
        ).strip()

        sensor_enabled = (
            request.POST.get("sensor_enabled") == "on"
        )

        exit_button_enabled = (
            request.POST.get("exit_button_enabled") == "on"
        )

        is_active = (
            request.POST.get("is_active") == "on"
        )

        # -----------------------------------------------------
        # VALIDATION
        # -----------------------------------------------------
        if not door_code:
            messages.error(
                request,
                "Door code is required.",
            )

        elif not name:
            messages.error(
                request,
                "Door name is required.",
            )

        else:

            # Check duplicate code excluding current door
            duplicate = Door.objects.filter(
                door_code__iexact=door_code
            ).exclude(
                id=door.id
            ).exists()

            if duplicate:

                messages.error(
                    request,
                    "Another door with this door code already exists.",
                )

            else:

                try:
                    unlock_duration = int(
                        unlock_duration
                    )

                    if unlock_duration < 1:
                        raise ValueError

                except (ValueError, TypeError):

                    messages.error(
                        request,
                        "Unlock duration must be a positive number.",
                    )

                else:

                    # -------------------------------------------------
                    # UPDATE DOOR
                    # -------------------------------------------------
                    door.door_code = door_code
                    door.name = name
                    door.location = location or None
                    door.lock_type = lock_type or None
                    door.unlock_duration_seconds = (
                        unlock_duration
                    )
                    door.sensor_enabled = sensor_enabled
                    door.exit_button_enabled = (
                        exit_button_enabled
                    )
                    door.is_active = is_active

                    # IMPORTANT:
                    # Existing database requires updated_at.
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

                    messages.success(
                        request,
                        f"Door '{door.name}' was updated successfully.",
                    )

                    return redirect(
                        "access_control:doors"
                    )

        # If validation failed, show the same form again.
        return render(
            request,
            "doors/edit.html",
            {
                "door": door,
            },
        )

    return render(
        request,
        "doors/edit.html",
        {
            "door": door,
        },
    )


@login_required
def door_toggle_status(request, door_id):
    """
    Activate or deactivate a door.
    """

    if request.method != "POST":
        return redirect(
            "access_control:doors"
        )

    door = get_object_or_404(
        Door,
        id=door_id,
    )

    door.is_active = not door.is_active
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
    Delete a door.
    """

    door = get_object_or_404(
        Door,
        id=door_id,
    )

    if request.method == "POST":

        door_name = door.name

        door.delete()

        messages.success(
            request,
            f"Door '{door_name}' was deleted successfully.",
        )

        return redirect(
            "access_control:doors"
        )

    return render(
        request,
        "doors/delete.html",
        {
            "door": door,
        },
    )