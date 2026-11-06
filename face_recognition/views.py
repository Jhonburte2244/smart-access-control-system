
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from employees.models import FaceTemplate
from doors.models import Door

from access_control.models import AccessLog
from access_control.services import AccessDecisionService

from .forms import FaceEnrollmentForm, FaceTemplateForm
from .services import FaceRecognitionService

@login_required
def face_template_list(request):

    templates = FaceTemplate.objects.select_related(
        "employee"
    ).all()

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------
    search_query = request.GET.get("q", "").strip()

    if search_query:

        templates = templates.filter(
            Q(employee__employee_number__icontains=search_query)
            | Q(employee__employee_id__icontains=search_query)
            | Q(employee__first_name__icontains=search_query)
            | Q(employee__middle_name__icontains=search_query)
            | Q(employee__last_name__icontains=search_query)
        )

    # ---------------------------------------------------------
    # STATUS FILTER
    # ---------------------------------------------------------
    status_filter = request.GET.get(
        "status",
        "",
    ).strip()

    if status_filter in [
        "active",
        "inactive",
        "blocked",
    ]:

        templates = templates.filter(
            status=status_filter
        )

    # ---------------------------------------------------------
    # STATISTICS
    # ---------------------------------------------------------
    all_templates = FaceTemplate.objects.all()

    total_templates = all_templates.count()

    active_templates = all_templates.filter(
        status="active"
    ).count()

    inactive_templates = all_templates.filter(
        status="inactive"
    ).count()

    blocked_templates = all_templates.filter(
        status="blocked"
    ).count()

    context = {
        "templates": templates,
        "total_templates": total_templates,
        "active_templates": active_templates,
        "inactive_templates": inactive_templates,
        "blocked_templates": blocked_templates,
        "search_query": search_query,
        "status_filter": status_filter,
    }

    return render(
        request,
        "face_recognition/list.html",
        context,
    )


@login_required
def face_template_add(request):

    if request.method == "POST":

        form = FaceEnrollmentForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            image_file = form.cleaned_data["image"]
            employee = form.cleaned_data["employee"]
            algorithm = form.cleaned_data["algorithm"]
            threshold = form.cleaned_data[
                "confidence_threshold"
            ]

            temp_path = default_storage.save(
                "face_temp/" + image_file.name,
                image_file,
            )

            absolute_path = default_storage.path(
                temp_path
            )

            try:

                service = FaceRecognitionService()

                template_data = (
                    service.create_template(
                        absolute_path
                    )
                )

                now = timezone.now()

                face_template = FaceTemplate(
                    employee=employee,
                    template_data=template_data,
                    algorithm=algorithm,
                    confidence_threshold=threshold,
                    status="active",
                    created_at=now,
                    updated_at=now,
                )

                face_template.save()

                messages.success(
                    request,
                    (
                        f"Face enrolled successfully for "
                        f"{employee.employee_number}."
                    ),
                )

                return redirect(
                    "face_recognition:face_template_detail",
                    pk=face_template.pk,
                )

            except ValueError as error:

                form.add_error(
                    "image",
                    str(error),
                )

            except Exception as error:

                form.add_error(
                    "image",
                    (
                        "Face enrollment failed: "
                        f"{error}"
                    ),
                )

            finally:

                if default_storage.exists(
                    temp_path
                ):
                    default_storage.delete(
                        temp_path
                    )

    else:

        form = FaceEnrollmentForm()

    return render(
        request,
        "face_recognition/form.html",
        {
            "form": form,
            "edit_mode": False,
            "enrollment_mode": True,
        },
    )


@login_required
def face_template_detail(request, pk):

    face_template = get_object_or_404(
        FaceTemplate.objects.select_related("employee"),
        pk=pk,
    )

    return render(
        request,
        "face_recognition/detail.html",
        {
            "face_template": face_template,
        },
    )


@login_required
def face_template_edit(request, pk):

    face_template = get_object_or_404(
        FaceTemplate,
        pk=pk,
    )

    if request.method == "POST":

        form = FaceTemplateForm(
            request.POST,
            instance=face_template,
        )

        if form.is_valid():

            face_template = form.save(
                commit=False
            )

            face_template.updated_at = timezone.now()

            face_template.save(
                update_fields=[
                    "employee",
                    "algorithm",
                    "confidence_threshold",
                    "status",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                "Face template updated successfully.",
            )

            return redirect(
                "face_recognition:face_template_detail",
                pk=face_template.pk,
            )

    else:

        form = FaceTemplateForm(
            instance=face_template,
        )

    return render(
        request,
        "face_recognition/form.html",
        {
            "form": form,
            "face_template": face_template,
            "edit_mode": True,
        },
    )


@login_required
def face_template_toggle_status(request, pk):

    face_template = get_object_or_404(
        FaceTemplate,
        pk=pk,
    )

    if face_template.status == "active":

        face_template.status = "inactive"

    else:

        face_template.status = "active"

    face_template.updated_at = timezone.now()

    face_template.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    messages.success(
        request,
        f"Face template status changed to {face_template.status}.",
    )

    return redirect(
        "face_recognition:face_template_list"
    )


@login_required
def face_template_delete(request, pk):

    face_template = get_object_or_404(
        FaceTemplate,
        pk=pk,
    )

    if request.method == "POST":

        face_template.delete()

        messages.success(
            request,
            "Face template deleted successfully.",
        )

        return redirect(
            "face_recognition:face_template_list"
        )

    return render(
        request,
        "face_recognition/detail.html",
        {
            "face_template": face_template,
            "confirm_delete": True,
        },
    )

@login_required
def recognize_face(request):

    result = None
    selected_door = None
    temp_path = None

    # =========================================================
    # LOAD ACTIVE DOORS
    # =========================================================

    doors = Door.objects.filter(
        is_active=True
    ).order_by("name")

    # =========================================================
    # HANDLE POST REQUEST
    # =========================================================

    if request.method == "POST":

        image = request.FILES.get("image")
        door_id = request.POST.get("door_id")

        # =====================================================
        # VALIDATE SELECTED DOOR
        # =====================================================

        if door_id:

            selected_door = (
                Door.objects
                .filter(
                    pk=door_id,
                    is_active=True,
                )
                .first()
            )

        # =====================================================
        # VALIDATE IMAGE
        # =====================================================

        if not image:

            messages.error(
                request,
                "Please select a face image."
            )

        # =====================================================
        # VALIDATE DOOR
        # =====================================================

        elif not selected_door:

            messages.error(
                request,
                "Please select a valid active access door."
            )

        else:

            try:

                # =================================================
                # SAVE TEMPORARY IMAGE
                # =================================================

                temp_path = default_storage.save(
                    "face_temp/" + image.name,
                    image,
                )

                absolute_path = default_storage.path(
                    temp_path
                )

                # =================================================
                # INITIALIZE FACE RECOGNITION SERVICE
                # =================================================

                service = FaceRecognitionService()

                # =================================================
                # LOAD ACTIVE FACE TEMPLATES
                # =================================================

                templates = (
                    FaceTemplate.objects
                    .filter(
                        status="active"
                    )
                    .select_related("employee")
                )

                # =================================================
                # FACE RECOGNITION
                # =================================================

                result = service.recognize_image(
                    absolute_path,
                    templates,
                )

                print("\n========================================")
                print("FACE RECOGNITION RESULT")
                print("========================================")
                print(
                    "Recognized:",
                    result.get("recognized")
                )
                print(
                    "Score:",
                    result.get("score")
                )
                print(
                    "Threshold:",
                    result.get("threshold")
                )

                # =================================================
                # FACE RECOGNIZED
                # =================================================

                if result.get("recognized"):

                    employee = result.get("employee")

                    print(
                        "Employee:",
                        employee
                    )

                    # =============================================
                    # ACCESS DECISION
                    # =============================================

                    access_result = (
                        AccessDecisionService.check_access(
                            employee,
                            selected_door,
                        )
                    )

                    # =============================================
                    # ADD ACCESS RESULT TO RECOGNITION RESULT
                    # =============================================

                    result["access"] = access_result

                    # =============================================
                    # DETERMINE ACTION
                    # =============================================

                    if access_result.get("granted"):

                        action = "granted"

                    else:

                        action = "deneid"

                    # =============================================
                    # ACCESS LOG
                    # =============================================

                    now = timezone.now()

                    print("\n========================================")
                    print("CREATING FACE ACCESS LOG")
                    print("========================================")
                    print(
                        "Employee:",
                        employee
                    )
                    print(
                        "Door:",
                        selected_door
                    )
                    print(
                        "Authentication: FACE"
                    )
                    print(
                        "Action:",
                        action
                    )
                    print(
                        "Score:",
                        result.get("score")
                    )
                    print(
                        "Reason:",
                        access_result.get("reason")
                    )

                    # =============================================
                    # CREATE LOG
                    # =============================================

                    log = AccessLog.objects.create(

                        employee=employee,

                        door=selected_door,

                        rfid_card=None,

                        authentication_method="FACE",

                        action=action,

                        reason=access_result.get(
                            "reason",
                            "Access decision completed.",
                        ),

                        confidence_score=round(
                            float(
                                result.get(
                                    "score",
                                    0,
                                )
                            ),
                            2,
                        ),

                        ip_address=request.META.get(
                            "REMOTE_ADDR"
                        ),

                        event_time=now,

                        created_at=now,
                    )

                    # =============================================
                    # CONFIRM LOG CREATED
                    # =============================================

                    print("\n========================================")
                    print("FACE ACCESS LOG CREATED")
                    print("========================================")
                    print(
                        "Log ID:",
                        log.id
                    )
                    print(
                        "Employee:",
                        log.employee.employee_number
                    )
                    print(
                        "Door:",
                        log.door.door_code
                    )
                    print(
                        "Authentication:",
                        log.authentication_method
                    )
                    print(
                        "Action:",
                        log.action
                    )
                    print(
                        "Confidence:",
                        log.confidence_score
                    )
                    print(
                        "========================================\n"
                    )

                # =================================================
                # FACE NOT RECOGNIZED
                # =================================================

                else:

                    print("\n========================================")
                    print("FACE NOT RECOGNIZED")
                    print("========================================")

                    # =============================================
                    # ACCESS RESULT
                    # =============================================

                    result["access"] = {

                        "granted": False,

                        "employee": None,

                        "door": selected_door,

                        "permission": None,

                        "access_rule": None,

                        "reason": "Face not recognized.",
                    }

                    # =============================================
                    # LOG UNKNOWN FACE
                    # =============================================

                    now = timezone.now()

                    log = AccessLog.objects.create(

                        employee=None,

                        door=selected_door,

                        rfid_card=None,

                        authentication_method="FACE",

                        action="DENIED",

                        reason="Face not recognized.",

                        confidence_score=round(
                            float(
                                result.get(
                                    "score",
                                    0,
                                )
                            ),
                            2,
                        ),

                        ip_address=request.META.get(
                            "REMOTE_ADDR"
                        ),

                        event_time=now,

                        created_at=now,
                    )

                    # =============================================
                    # CONFIRM UNKNOWN FACE LOG
                    # =============================================

                    print(
                        "UNKNOWN FACE ACCESS LOG CREATED"
                    )

                    print(
                        "Log ID:",
                        log.id
                    )

                    print(
                        "Door:",
                        selected_door.door_code
                    )

                    print(
                        "Action:",
                        log.action
                    )

                    print(
                        "========================================\n"
                    )

            # =====================================================
            # FACE VALIDATION ERROR
            # =====================================================

            except ValueError as error:

                messages.error(
                    request,
                    str(error),
                )

                print(
                    "FACE VALIDATION ERROR:",
                    error
                )

            # =====================================================
            # DATABASE / RECOGNITION ERROR
            # =====================================================

            except Exception as error:

                messages.error(
                    request,
                    f"Recognition or access logging failed: {error}",
                )

                print(
                    "FACE RECOGNITION / ACCESS LOG ERROR:",
                    error
                )

            # =====================================================
            # DELETE TEMPORARY IMAGE
            # =====================================================

            finally:

                if (
                    temp_path
                    and default_storage.exists(
                        temp_path
                    )
                ):

                    default_storage.delete(
                        temp_path
                    )

    # =========================================================
    # RENDER PAGE
    # =========================================================

    return render(
        request,
        "face_recognition/recognize.html",
        {
            "result": result,
            "doors": doors,
            "selected_door": selected_door,
        },
    )
