from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from employees.models import Employee, RFIDCard

@login_required
def rfid_card_list(request):

    cards = (
        RFIDCard.objects
        .select_related("employee")
        .order_by("-created_at")
    )

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        cards = cards.filter(
            Q(card_uid__icontains=search)
            | Q(card_number__icontains=search)
            | Q(card_type__icontains=search)
            | Q(employee__employee_number__icontains=search)
            | Q(employee__first_name__icontains=search)
            | Q(employee__middle_name__icontains=search)
            | Q(employee__last_name__icontains=search)
        )

    if status:
        cards = cards.filter(
            status__iexact=status
        )

    total_cards = cards.count()

    active_cards = cards.filter(
        status__iexact="active"
    ).count()

    inactive_cards = cards.filter(
        status__iexact="inactive"
    ).count()

    context = {
        "cards": cards,
        "total_cards": total_cards,
        "active_cards": active_cards,
        "inactive_cards": inactive_cards,
        "search": search,
        "selected_status": status,
    }

    return render(
        request,
        "rfid_cards/list.html",
        context
    )


@login_required
def rfid_card_add(request):

    employees = Employee.objects.all().order_by("employee_number")

    if request.method == "POST":

        card_uid = request.POST.get("card_uid", "").strip()
        card_number = request.POST.get("card_number", "").strip()
        employee_id = request.POST.get("employee_id", "").strip()
        card_type = request.POST.get("card_type", "RFID").strip()
        expires_at = request.POST.get("expires_at", "").strip()
        status = request.POST.get("status", "active").strip()

        # -----------------------------
        # Validate Card UID
        # -----------------------------
        if not card_uid:
            messages.error(request, "Card UID is required.")
            return render(
                request,
                "rfid_cards/add.html",
                {"employees": employees},
            )

        # -----------------------------
        # Check duplicate UID
        # -----------------------------
        if RFIDCard.objects.filter(card_uid=card_uid).exists():
            messages.error(
                request,
                f"RFID card UID '{card_uid}' already exists."
            )

            return render(
                request,
                "rfid_cards/add.html",
                {"employees": employees},
            )

        # -----------------------------
        # Check duplicate card number
        # -----------------------------
        if card_number and RFIDCard.objects.filter(
            card_number=card_number
        ).exists():

            messages.error(
                request,
                f"Card number '{card_number}' already exists."
            )

            return render(
                request,
                "rfid_cards/add.html",
                {"employees": employees},
            )

        # -----------------------------
        # Employee
        # -----------------------------
        employee = None

        if employee_id:
            try:
                employee = Employee.objects.get(id=employee_id)
            except Employee.DoesNotExist:
                messages.error(
                    request,
                    "Selected employee does not exist."
                )

                return render(
                    request,
                    "rfid_cards/add.html",
                    {"employees": employees},
                )

        # -----------------------------
        # Expiry date
        # -----------------------------
        expires_at_value = None

        if expires_at:
            try:
                from datetime import datetime

                expires_at_value = datetime.strptime(
                    expires_at,
                    "%Y-%m-%d"
                )

            except ValueError:
                messages.error(
                    request,
                    "Invalid expiry date."
                )

                return render(
                    request,
                    "rfid_cards/add.html",
                    {"employees": employees},
                )

        # -----------------------------
        # Create RFID Card
        # -----------------------------
        card = RFIDCard(
            card_uid=card_uid,
            card_number=card_number or None,
            employee=employee,
            card_type=card_type,
            issued_at=timezone.now(),
            expires_at=expires_at_value,
            status=status,
            created_at=timezone.now(),
        )

        card.save()

        messages.success(
            request,
            f"RFID card '{card_uid}' added successfully."
        )

        return redirect("rfid_cards:rfid_card_list")

    return render(
        request,
        "rfid_cards/add.html",
        {"employees": employees},
    )

@login_required
def rfid_card_edit(request, card_id):

    card = get_object_or_404(
        RFIDCard,
        id=card_id
    )

    employees = Employee.objects.all().order_by(
        "employee_number"
    )

    if request.method == "POST":

        card_uid = request.POST.get(
            "card_uid",
            ""
        ).strip()

        card_number = request.POST.get(
            "card_number",
            ""
        ).strip()

        employee_id = request.POST.get(
            "employee_id",
            ""
        ).strip()

        card_type = request.POST.get(
            "card_type",
            "RFID"
        ).strip()

        expires_at = request.POST.get(
            "expires_at",
            ""
        ).strip()

        status = request.POST.get(
            "status",
            "active"
        ).strip()

        # --------------------------------
        # Validate Card UID
        # --------------------------------

        if not card_uid:

            messages.error(
                request,
                "Card UID is required."
            )

            return render(
                request,
                "rfid_cards/edit.html",
                {
                    "card": card,
                    "employees": employees,
                }
            )

        # --------------------------------
        # Check duplicate UID
        # --------------------------------

        if RFIDCard.objects.filter(
            card_uid=card_uid
        ).exclude(
            id=card.id
        ).exists():

            messages.error(
                request,
                f"RFID card UID '{card_uid}' already exists."
            )

            return render(
                request,
                "rfid_cards/edit.html",
                {
                    "card": card,
                    "employees": employees,
                }
            )

        # --------------------------------
        # Check duplicate card number
        # --------------------------------

        if card_number and RFIDCard.objects.filter(
            card_number=card_number
        ).exclude(
            id=card.id
        ).exists():

            messages.error(
                request,
                f"Card number '{card_number}' already exists."
            )

            return render(
                request,
                "rfid_cards/edit.html",
                {
                    "card": card,
                    "employees": employees,
                }
            )

        # --------------------------------
        # Employee
        # --------------------------------

        employee = None

        if employee_id:

            try:

                employee = Employee.objects.get(
                    id=employee_id
                )

            except Employee.DoesNotExist:

                messages.error(
                    request,
                    "Selected employee does not exist."
                )

                return render(
                    request,
                    "rfid_cards/edit.html",
                    {
                        "card": card,
                        "employees": employees,
                    }
                )

        # --------------------------------
        # Expiry date
        # --------------------------------

        expires_at_value = None

        if expires_at:

            from datetime import datetime

            try:

                expires_at_value = datetime.strptime(
                    expires_at,
                    "%Y-%m-%d"
                )

            except ValueError:

                messages.error(
                    request,
                    "Invalid expiry date."
                )

                return render(
                    request,
                    "rfid_cards/edit.html",
                    {
                        "card": card,
                        "employees": employees,
                    }
                )

        # --------------------------------
        # Update card
        # --------------------------------

        card.card_uid = card_uid
        card.card_number = card_number or None
        card.employee = employee
        card.card_type = card_type
        card.expires_at = expires_at_value
        card.status = status

        card.save()

        messages.success(
            request,
            f"RFID card '{card_uid}' updated successfully."
        )

        return redirect(
            "rfid_cards:rfid_card_list"
        )

    # --------------------------------
    # GET request
    # --------------------------------

    return render(
        request,
        "rfid_cards/edit.html",
        {
            "card": card,
            "employees": employees,
        }
    )


@login_required
def rfid_card_toggle_status(request, card_id):

    card = get_object_or_404(
        RFIDCard,
        id=card_id
    )

    if request.method == "POST":

        if card.status.lower() == "active":
            card.status = "inactive"
            message = "RFID card deactivated successfully."

        else:
            card.status = "active"
            message = "RFID card activated successfully."

        card.save()

        messages.success(
            request,
            message
        )

    return redirect(
        "rfid_cards:rfid_card_list"
    )




@login_required
def rfid_card_delete(request, card_id):

    if request.method != "POST":
        return redirect("rfid_cards:rfid_card_list")

    card = get_object_or_404(
        RFIDCard,
        id=card_id
    )

    card_uid = card.card_uid

    card.delete()

    messages.success(
        request,
        f"RFID card '{card_uid}' deleted successfully."
    )

    return redirect(
        "rfid_cards:rfid_card_list"
    )