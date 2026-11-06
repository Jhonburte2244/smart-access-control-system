import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import (
    HttpResponseNotAllowed,
    JsonResponse,
)
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Device

@login_required
def device_list(request):
    """
    Display all registered devices.
    Supports search and status filtering.
    """

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip().lower()

    devices = Device.objects.all()

    # Search
    if search:
        devices = devices.filter(
            Q(device_code__icontains=search)
            | Q(device_name__icontains=search)
            | Q(device_type__icontains=search)
            | Q(location__icontains=search)
            | Q(ip_address__icontains=search)
            | Q(mac_address__icontains=search)
        )

    # Status filter
    if status == "active":
        devices = devices.filter(is_active=True)

    elif status == "inactive":
        devices = devices.filter(is_active=False)

    total_devices = Device.objects.count()
    active_devices = Device.objects.filter(is_active=True).count()
    inactive_devices = Device.objects.filter(is_active=False).count()

    context = {
        "devices": devices,
        "search": search,
        "status": status,
        "total_devices": total_devices,
        "active_devices": active_devices,
        "inactive_devices": inactive_devices,
    }

    return render(
        request,
        "devices/list.html",
        context,
    )


@login_required
def device_add(request):
    """
    Register a new ESP32/device.
    """

    if request.method == "POST":

        device_code = request.POST.get("device_code", "").strip()
        device_name = request.POST.get("device_name", "").strip()
        device_type = request.POST.get(
            "device_type",
            "ESP32",
        ).strip()
        location = request.POST.get("location", "").strip()
        ip_address = request.POST.get("ip_address", "").strip()
        mac_address = request.POST.get("mac_address", "").strip()
        firmware_version = request.POST.get(
            "firmware_version",
            "",
        ).strip()

        # Required fields
        if not device_code:
            messages.error(
                request,
                "Device code is required.",
            )

        elif not device_name:
            messages.error(
                request,
                "Device name is required.",
            )

        elif Device.objects.filter(
            device_code=device_code
        ).exists():
            messages.error(
                request,
                f"Device code '{device_code}' already exists.",
            )

        else:

            device = Device(
                device_code=device_code,
                device_name=device_name,
                device_type=device_type or "ESP32",
                location=location or None,
                ip_address=ip_address or None,
                mac_address=mac_address or None,
                firmware_version=firmware_version or None,
                is_active=True,
            )

            try:
                device.save(force_insert=True)

                messages.success(
                    request,
                    f"Device '{device_code}' was registered successfully.",
                )

                return redirect(
                    "devices:device_list"
                )

            except Exception as e:
                messages.error(
                    request,
                    f"Unable to register device: {e}",
                )

    context = {
        "device": None,
        "edit_mode": False,
    }

    return render(
        request,
        "devices/form.html",
        context,
    )


@login_required
def device_detail(request, device_id):
    """
    Display device details.
    """

    device = get_object_or_404(
        Device,
        id=device_id,
    )

    context = {
        "device": device,
    }

    return render(
        request,
        "devices/detail.html",
        context,
    )


@login_required
def device_edit(request, device_id):
    """
    Edit device information.
    """

    device = get_object_or_404(
        Device,
        id=device_id,
    )

    if request.method == "POST":

        device_code = request.POST.get(
            "device_code",
            "",
        ).strip()

        device_name = request.POST.get(
            "device_name",
            "",
        ).strip()

        device_type = request.POST.get(
            "device_type",
            "ESP32",
        ).strip()

        location = request.POST.get(
            "location",
            "",
        ).strip()

        ip_address = request.POST.get(
            "ip_address",
            "",
        ).strip()

        mac_address = request.POST.get(
            "mac_address",
            "",
        ).strip()

        firmware_version = request.POST.get(
            "firmware_version",
            "",
        ).strip()

        # Required fields
        if not device_code:
            messages.error(
                request,
                "Device code is required.",
            )

        elif not device_name:
            messages.error(
                request,
                "Device name is required.",
            )

        elif Device.objects.filter(
            device_code=device_code
        ).exclude(
            id=device.id
        ).exists():

            messages.error(
                request,
                f"Device code '{device_code}' already exists.",
            )

        else:

            device.device_code = device_code
            device.device_name = device_name
            device.device_type = device_type or "ESP32"
            device.location = location or None
            device.ip_address = ip_address or None
            device.mac_address = mac_address or None
            device.firmware_version = (
                firmware_version or None
            )

            try:
                device.save(
                    force_update=True
                )

                messages.success(
                    request,
                    "Device updated successfully.",
                )

                return redirect(
                    "devices:device_detail",
                    device_id=device.id,
                )

            except Exception as e:
                messages.error(
                    request,
                    f"Unable to update device: {e}",
                )

    context = {
        "device": device,
        "edit_mode": True,
    }

    return render(
        request,
        "devices/form.html",
        context,
    )


@login_required
def device_toggle_status(request, device_id):
    """
    Activate or deactivate a device.
    """

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    device = get_object_or_404(
        Device,
        id=device_id,
    )

    device.is_active = not device.is_active

    device.save(
        force_update=True,
        update_fields=[
            "is_active",
            "updated_at",
        ],
    )

    if device.is_active:
        messages.success(
            request,
            f"{device.device_code} is now active.",
        )
    else:
        messages.warning(
            request,
            f"{device.device_code} is now inactive.",
        )

    return redirect(
        "devices:device_list"
    )


@login_required
def device_delete(request, device_id):
    """
    Delete a device.
    """

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    device = get_object_or_404(
        Device,
        id=device_id,
    )

    device_code = device.device_code

    device.delete()

    messages.success(
        request,
        f"Device '{device_code}' was deleted.",
    )

    return redirect(
        "devices:device_list"
    )
    
@csrf_exempt
def device_register_api(request):
    """
    ESP32 device registration / heartbeat API.

    The ESP32 sends:
        device_code
        device_name
        device_type
        ip_address
        mac_address
        firmware_version
    """

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "error": "POST method required.",
            },
            status=405,
        )

    try:
        data = json.loads(
            request.body.decode("utf-8")
        )

    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {
                "success": False,
                "error": "Invalid JSON data.",
            },
            status=400,
        )

    device_code = str(
        data.get("device_code", "")
    ).strip()

    if not device_code:
        return JsonResponse(
            {
                "success": False,
                "error": "device_code is required.",
            },
            status=400,
        )

    try:
        device = Device.objects.get(
            device_code=device_code
        )

    except Device.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "error": "Device is not registered.",
                "device_code": device_code,
            },
            status=404,
        )

    # Do not allow inactive devices to communicate
    if not device.is_active:
        return JsonResponse(
            {
                "success": False,
                "error": "Device is inactive.",
                "device_code": device.device_code,
            },
            status=403,
        )

    # Update information received from ESP32
    device.ip_address = (
        data.get("ip_address")
        or request.META.get("REMOTE_ADDR")
        or None
    )

    device.mac_address = (
        str(data.get("mac_address", "")).strip()
        or device.mac_address
        or None
    )

    device.firmware_version = (
        str(
            data.get(
                "firmware_version",
                "",
            )
        ).strip()
        or device.firmware_version
        or None
    )

    device.last_seen = timezone.now()

    device.save(
        force_update=True,
        update_fields=[
            "ip_address",
            "mac_address",
            "firmware_version",
            "last_seen",
            "updated_at",
        ],
    )

    return JsonResponse(
        {
            "success": True,
            "message": "Device registered successfully.",
            "device": {
                "id": device.id,
                "device_code": device.device_code,
                "device_name": device.device_name,
                "device_type": device.device_type,
                "location": device.location,
                "ip_address": str(
                    device.ip_address
                )
                if device.ip_address
                else None,
                "mac_address": device.mac_address,
                "firmware_version": (
                    device.firmware_version
                ),
                "is_active": device.is_active,
                "last_seen": (
                    device.last_seen.isoformat()
                    if device.last_seen
                    else None
                ),
            },
        },
        status=200,
    )