import io
import calendar
from datetime import datetime, timedelta

from django.db.models import Q
from django.http import HttpResponse
from employees.models import Employee
from attendance.models import Attendance
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

@login_required
def attendance_list(request):

    today = timezone.localdate()

    # =====================================================
    # FILTER VALUES
    # =====================================================

    selected_date = request.GET.get(
        "date",
        today.strftime("%Y-%m-%d")
    )

    employee_search = request.GET.get(
        "employee",
        ""
    ).strip()

    status_filter = request.GET.get(
        "status",
        ""
    ).strip()

    department_filter = request.GET.get(
        "department",
        ""
    ).strip()

    # =====================================================
    # BASE QUERY
    # =====================================================

    attendance_records = (
        Attendance.objects
        .select_related("employee")
        .order_by(
            "-attendance_date",
            "-check_in"
        )
    )

    # =====================================================
    # DATE FILTER
    # =====================================================

    if selected_date:
        attendance_records = attendance_records.filter(
            attendance_date=selected_date
        )

    # =====================================================
    # EMPLOYEE SEARCH
    # =====================================================

    if employee_search:

        attendance_records = attendance_records.filter(
            Q(employee__first_name__icontains=employee_search)
            |
            Q(employee__middle_name__icontains=employee_search)
            |
            Q(employee__last_name__icontains=employee_search)
            |
            Q(employee__employee_number__icontains=employee_search)
        )

    # =====================================================
    # STATUS FILTER
    # =====================================================

    if status_filter:
        attendance_records = attendance_records.filter(
            status=status_filter
        )

    # =====================================================
    # DEPARTMENT FILTER
    # =====================================================

    if department_filter:

        attendance_records = attendance_records.filter(
            employee__department_id=department_filter
        )

    # =====================================================
    # TODAY'S STATISTICS
    # =====================================================

    today_records = Attendance.objects.filter(
        attendance_date=today
    )

    # Employee model uses "status", not "is_active"
    total_employees = Employee.objects.filter(
        status="active"
    ).count()

    present_today = today_records.filter(
        status="present"
    ).count()

    late_today = today_records.filter(
        status="late"
    ).count()

    absent_today = today_records.filter(
        status="absent"
    ).count()

    early_leave_today = today_records.filter(
        early_leave_minutes__gt=0
    ).count()

    leave_today = today_records.filter(
        status="leave"
    ).count()

    currently_inside = today_records.filter(
        check_in__isnull=False,
        check_out__isnull=True
    ).count()

    # =====================================================
    # ATTENDANCE RATE
    # =====================================================

    attendance_rate = 0

    if total_employees > 0:

        attendance_rate = round(
            (
                today_records.exclude(
                    status__in=["absent", "leave"]
                ).count()
                / total_employees
            ) * 100,
            1
        )

    # =====================================================
    # DEPARTMENTS
    # =====================================================

    departments = (
        Employee.objects
        .filter(
            status="active",
            department__isnull=False
        )
        .values(
            "department_id",
            "department__name"
        )
        .distinct()
        .order_by(
            "department__name"
        )
    )

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        "attendance": attendance_records,

        # Filters
        "selected_date": selected_date,
        "employee_search": employee_search,
        "status_filter": status_filter,
        "department_filter": department_filter,

        # Statistics
        "total_employees": total_employees,
        "present_today": present_today,
        "late_today": late_today,
        "absent_today": absent_today,
        "early_leave_today": early_leave_today,
        "leave_today": leave_today,
        "currently_inside": currently_inside,
        "attendance_rate": attendance_rate,

        # Department list
        "departments": departments,
    }

    return render(
        request,
        "attendance/list.html",
        context
    )

@login_required
def attendance_weekly(request):
    today = timezone.localdate()

    # Selected date is used to determine the week
    selected_date = parse_date(
        request.GET.get("date", today.isoformat())
    ) or today

    # Monday to Sunday
    week_start = selected_date - timedelta(days=selected_date.weekday())
    week_end = week_start + timedelta(days=6)

    employee_search = request.GET.get("employee", "").strip()
    department_filter = request.GET.get("department", "").strip()
    status_filter = request.GET.get("status", "").strip()

    # Active employees
    employees = (
        Employee.objects
        .filter(status="active")
        .select_related("department")
        .order_by("first_name", "middle_name", "last_name")
    )

    # Employee search
    if employee_search:
        employees = employees.filter(
            Q(employee_id__icontains=employee_search)
            | Q(employee_number__icontains=employee_search)
            | Q(first_name__icontains=employee_search)
            | Q(middle_name__icontains=employee_search)
            | Q(last_name__icontains=employee_search)
        )

    # Department filter
    if department_filter:
        employees = employees.filter(
            department_id=department_filter
        )

    # Attendance records for the selected week
    records = (
        Attendance.objects
        .filter(
            attendance_date__range=(week_start, week_end)
        )
        .select_related("employee")
    )

    # Group attendance records by employee and date
    attendance_map = {}

    for record in records:
        attendance_map[
            (record.employee_id, record.attendance_date)
        ] = record

    # Days of the week
    week_days = [
        week_start + timedelta(days=i)
        for i in range(7)
    ]

    weekly_rows = []

    for employee in employees:

        daily_records = []
        present_count = 0
        late_count = 0
        absent_count = 0
        leave_count = 0
        worked_minutes = 0
        overtime_minutes = 0

        for day in week_days:

            record = attendance_map.get(
                (employee.id, day)
            )

            if record:
                status = (record.status or "").lower()

                if status == "present":
                    present_count += 1

                elif status == "late":
                    late_count += 1

                elif status == "absent":
                    absent_count += 1

                elif status == "leave":
                    leave_count += 1

                worked_minutes += record.worked_minutes or 0
                overtime_minutes += record.overtime_minutes or 0

            daily_records.append({
                "date": day,
                "record": record,
            })

        recorded_days = (
            present_count
            + late_count
            + absent_count
            + leave_count
        )

        attendance_rate = 0

        if recorded_days > 0:
            attendance_rate = round(
                (
                    (present_count + late_count)
                    / recorded_days
                ) * 100,
                1
            )

        # Optional status filter
        if status_filter:
            employee_has_status = any(
                item["record"]
                and item["record"].status.lower() == status_filter.lower()
                for item in daily_records
            )

            if not employee_has_status:
                continue

        weekly_rows.append({
            "employee": employee,
            "days": daily_records,
            "present_count": present_count,
            "late_count": late_count,
            "absent_count": absent_count,
            "leave_count": leave_count,
            "attendance_rate": attendance_rate,
            "worked_minutes": worked_minutes,
            "overtime_minutes": overtime_minutes,
        })

    # Departments
    departments = (
        Employee.objects
        .filter(
            status="active",
            department__isnull=False
        )
        .values(
            "department_id",
            "department__name"
        )
        .distinct()
        .order_by("department__name")
    )

    # Weekly summary
    total_employees = len(weekly_rows)

    total_present = sum(
        row["present_count"]
        for row in weekly_rows
    )

    total_late = sum(
        row["late_count"]
        for row in weekly_rows
    )

    total_absent = sum(
        row["absent_count"]
        for row in weekly_rows
    )

    total_leave = sum(
        row["leave_count"]
        for row in weekly_rows
    )

    total_worked_minutes = sum(
        row["worked_minutes"]
        for row in weekly_rows
    )

    total_overtime_minutes = sum(
        row["overtime_minutes"]
        for row in weekly_rows
    )

    context = {
        "weekly_rows": weekly_rows,
        "week_start": week_start,
        "week_end": week_end,
        "selected_date": selected_date,

        "week_days": week_days,

        "employee_search": employee_search,
        "department_filter": department_filter,
        "status_filter": status_filter,

        "departments": departments,

        "total_employees": total_employees,
        "total_present": total_present,
        "total_late": total_late,
        "total_absent": total_absent,
        "total_leave": total_leave,
        "total_worked_minutes": total_worked_minutes,
        "total_overtime_minutes": total_overtime_minutes,
    }

    return render(
        request,
        "attendance/weekly.html",
        context
    )




@login_required
def attendance_monthly(request):
    today = timezone.localdate()

    # ---------------------------------------------------------
    # Selected month
    # ---------------------------------------------------------

    selected_date = parse_date(
        request.GET.get("date", today.isoformat())
    ) or today

    year = selected_date.year
    month = selected_date.month

    days_in_month = calendar.monthrange(year, month)[1]

    month_start = selected_date.replace(day=1)
    month_end = selected_date.replace(day=days_in_month)

    # ---------------------------------------------------------
    # Filters
    # ---------------------------------------------------------

    employee_search = request.GET.get("employee", "").strip()
    department_filter = request.GET.get("department", "").strip()
    status_filter = request.GET.get("status", "").strip()

    # ---------------------------------------------------------
    # Active employees
    # ---------------------------------------------------------

    employees = (
        Employee.objects
        .filter(status="active")
        .select_related("department")
        .order_by(
            "first_name",
            "middle_name",
            "last_name"
        )
    )

    # Employee search
    if employee_search:
        employees = employees.filter(
            Q(employee_id__icontains=employee_search)
            | Q(employee_number__icontains=employee_search)
            | Q(first_name__icontains=employee_search)
            | Q(middle_name__icontains=employee_search)
            | Q(last_name__icontains=employee_search)
        )

    # Department filter
    if department_filter:
        employees = employees.filter(
            department_id=department_filter
        )

    # ---------------------------------------------------------
    # Attendance records for selected month
    # ---------------------------------------------------------

    records = (
        Attendance.objects
        .filter(
            attendance_date__range=(
                month_start,
                month_end
            )
        )
        .select_related("employee")
    )

    # ---------------------------------------------------------
    # Map records by employee and date
    # ---------------------------------------------------------

    attendance_map = {}

    for record in records:
        attendance_map[
            (record.employee_id, record.attendance_date)
        ] = record

    # ---------------------------------------------------------
    # Build monthly employee rows
    # ---------------------------------------------------------

    month_days = [
        month_start + timedelta(days=i)
        for i in range(days_in_month)
    ]

    monthly_rows = []

    for employee in employees:

        daily_records = []

        present_count = 0
        late_count = 0
        absent_count = 0
        leave_count = 0

        worked_minutes = 0
        overtime_minutes = 0

        for day in month_days:

            record = attendance_map.get(
                (employee.id, day)
            )

            if record:

                status = (record.status or "").lower()

                if status == "present":
                    present_count += 1

                elif status == "late":
                    late_count += 1

                elif status == "absent":
                    absent_count += 1

                elif status == "leave":
                    leave_count += 1

                worked_minutes += (
                    record.worked_minutes or 0
                )

                overtime_minutes += (
                    record.overtime_minutes or 0
                )

            daily_records.append({
                "date": day,
                "record": record,
            })

        # -----------------------------------------------------
        # Attendance percentage
        # -----------------------------------------------------

        recorded_days = (
            present_count
            + late_count
            + absent_count
            + leave_count
        )

        attendance_rate = 0

        if recorded_days > 0:
            attendance_rate = round(
                (
                    (present_count + late_count)
                    / recorded_days
                ) * 100,
                1
            )

        # -----------------------------------------------------
        # Status filter
        # -----------------------------------------------------

        if status_filter:

            employee_has_status = any(
                item["record"]
                and (
                    item["record"].status or ""
                ).lower() == status_filter.lower()
                for item in daily_records
            )

            if not employee_has_status:
                continue

        monthly_rows.append({
            "employee": employee,
            "days": daily_records,

            "present_count": present_count,
            "late_count": late_count,
            "absent_count": absent_count,
            "leave_count": leave_count,

            "attendance_rate": attendance_rate,

            "worked_minutes": worked_minutes,
            "overtime_minutes": overtime_minutes,
        })

    # ---------------------------------------------------------
    # Departments
    # ---------------------------------------------------------

    departments = (
        Employee.objects
        .filter(
            status="active",
            department__isnull=False
        )
        .values(
            "department_id",
            "department__name"
        )
        .distinct()
        .order_by("department__name")
    )

    # ---------------------------------------------------------
    # Monthly summary
    # ---------------------------------------------------------

    total_employees = len(monthly_rows)

    total_present = sum(
        row["present_count"]
        for row in monthly_rows
    )

    total_late = sum(
        row["late_count"]
        for row in monthly_rows
    )

    total_absent = sum(
        row["absent_count"]
        for row in monthly_rows
    )

    total_leave = sum(
        row["leave_count"]
        for row in monthly_rows
    )

    total_worked_minutes = sum(
        row["worked_minutes"]
        for row in monthly_rows
    )

    total_overtime_minutes = sum(
        row["overtime_minutes"]
        for row in monthly_rows
    )

    # ---------------------------------------------------------
    # Context
    # ---------------------------------------------------------

    context = {
        "monthly_rows": monthly_rows,

        "month_start": month_start,
        "month_end": month_end,
        "selected_date": selected_date,

        "month_days": month_days,

        "employee_search": employee_search,
        "department_filter": department_filter,
        "status_filter": status_filter,

        "departments": departments,

        "total_employees": total_employees,
        "total_present": total_present,
        "total_late": total_late,
        "total_absent": total_absent,
        "total_leave": total_leave,

        "total_worked_minutes": total_worked_minutes,
        "total_overtime_minutes": total_overtime_minutes,
    }

    return render(
        request,
        "attendance/monthly.html",
        context
    )
    
@login_required
def attendance_departments(request):
    today = timezone.localdate()

    period = request.GET.get("period", "daily").strip().lower()
    if period not in ["daily", "weekly", "monthly"]:
        period = "daily"

    date_param = request.GET.get("date", "").strip()

    # ---------------------------------------------------------
    # Determine reporting period
    # ---------------------------------------------------------

    selected_date = today

    if period == "monthly":
        try:
            selected_date = datetime.strptime(
                date_param,
                "%Y-%m"
            ).date()
        except (ValueError, TypeError):
            selected_date = today.replace(day=1)

        period_start = selected_date.replace(day=1)

        days_in_month = calendar.monthrange(
            selected_date.year,
            selected_date.month
        )[1]

        period_end = selected_date.replace(
            day=days_in_month
        )

    else:
        if date_param:
            parsed_date = parse_date(date_param)
            if parsed_date:
                selected_date = parsed_date

        if period == "weekly":
            period_start = (
                selected_date
                - timedelta(days=selected_date.weekday())
            )
            period_end = period_start + timedelta(days=6)

        else:
            period_start = selected_date
            period_end = selected_date

    # ---------------------------------------------------------
    # Department filter
    # ---------------------------------------------------------

    department_filter = request.GET.get(
        "department",
        ""
    ).strip()

    # ---------------------------------------------------------
    # Active employees
    # ---------------------------------------------------------

    employees = (
        Employee.objects
        .filter(
            status="active",
            department__isnull=False,
        )
        .select_related("department")
        .order_by(
            "department__name",
            "first_name",
            "middle_name",
            "last_name",
        )
    )

    if department_filter:
        employees = employees.filter(
            department_id=department_filter
        )

    # ---------------------------------------------------------
    # Attendance records
    # ---------------------------------------------------------

    records = (
        Attendance.objects
        .filter(
            attendance_date__range=(
                period_start,
                period_end,
            )
        )
        .select_related("employee")
    )

    # ---------------------------------------------------------
    # Group attendance by employee
    # ---------------------------------------------------------

    employee_records = {}

    for record in records:
        employee_records.setdefault(
            record.employee_id,
            []
        ).append(record)

    # ---------------------------------------------------------
    # Build department summaries
    # ---------------------------------------------------------

    department_data = {}

    for employee in employees:

        department = employee.department

        if not department:
            continue

        department_id = department.id

        if department_id not in department_data:
            department_data[department_id] = {
                "department": department,
                "employees": 0,
                "present": 0,
                "late": 0,
                "absent": 0,
                "leave": 0,
                "recorded_days": 0,
                "worked_minutes": 0,
                "overtime_minutes": 0,
                "employee_details": [],
            }

        data = department_data[department_id]

        data["employees"] += 1

        employee_present = 0
        employee_late = 0
        employee_absent = 0
        employee_leave = 0
        employee_worked = 0
        employee_overtime = 0

        for record in employee_records.get(
            employee.id,
            []
        ):

            status = (record.status or "").lower()

            if status == "present":
                data["present"] += 1
                employee_present += 1

            elif status == "late":
                data["late"] += 1
                employee_late += 1

            elif status == "absent":
                data["absent"] += 1
                employee_absent += 1

            elif status == "leave":
                data["leave"] += 1
                employee_leave += 1

            if status in [
                "present",
                "late",
                "absent",
                "leave",
            ]:
                data["recorded_days"] += 1

            worked = record.worked_minutes or 0
            overtime = record.overtime_minutes or 0

            data["worked_minutes"] += worked
            data["overtime_minutes"] += overtime

            employee_worked += worked
            employee_overtime += overtime

        employee_recorded_days = (
            employee_present
            + employee_late
            + employee_absent
            + employee_leave
        )

        employee_attendance_rate = 0

        if employee_recorded_days > 0:
            employee_attendance_rate = round(
                (
                    (
                        employee_present
                        + employee_late
                    )
                    / employee_recorded_days
                )
                * 100,
                1,
            )

        data["employee_details"].append({
            "employee": employee,
            "present": employee_present,
            "late": employee_late,
            "absent": employee_absent,
            "leave": employee_leave,
            "worked_minutes": employee_worked,
            "overtime_minutes": employee_overtime,
            "attendance_rate": employee_attendance_rate,
        })

    # ---------------------------------------------------------
    # Final department calculations
    # ---------------------------------------------------------

    department_rows = []

    for data in department_data.values():

        attendance_rate = 0

        if data["recorded_days"] > 0:
            attendance_rate = round(
                (
                    (
                        data["present"]
                        + data["late"]
                    )
                    / data["recorded_days"]
                )
                * 100,
                1,
            )

        data["attendance_rate"] = attendance_rate

        department_rows.append(data)

    department_rows.sort(
        key=lambda x: x["department"].name.lower()
    )

    # ---------------------------------------------------------
    # Department list for filter
    # ---------------------------------------------------------

    departments = (
        Employee.objects
        .filter(
            status="active",
            department__isnull=False,
        )
        .values(
            "department_id",
            "department__name",
        )
        .distinct()
        .order_by("department__name")
    )

    # ---------------------------------------------------------
    # Overall totals
    # ---------------------------------------------------------

    total_departments = len(department_rows)

    total_employees = sum(
        row["employees"]
        for row in department_rows
    )

    total_present = sum(
        row["present"]
        for row in department_rows
    )

    total_late = sum(
        row["late"]
        for row in department_rows
    )

    total_absent = sum(
        row["absent"]
        for row in department_rows
    )

    total_leave = sum(
        row["leave"]
        for row in department_rows
    )

    total_worked_minutes = sum(
        row["worked_minutes"]
        for row in department_rows
    )

    total_overtime_minutes = sum(
        row["overtime_minutes"]
        for row in department_rows
    )

    total_recorded_days = sum(
        row["recorded_days"]
        for row in department_rows
    )

    overall_attendance_rate = 0

    if total_recorded_days > 0:
        overall_attendance_rate = round(
            (
                (
                    total_present
                    + total_late
                )
                / total_recorded_days
            )
            * 100,
            1,
        )

    context = {
        "department_rows": department_rows,
        "departments": departments,

        "period": period,
        "selected_date": selected_date,
        "period_start": period_start,
        "period_end": period_end,

        "department_filter": department_filter,

        "total_departments": total_departments,
        "total_employees": total_employees,
        "total_present": total_present,
        "total_late": total_late,
        "total_absent": total_absent,
        "total_leave": total_leave,
        "overall_attendance_rate": overall_attendance_rate,
        "total_worked_minutes": total_worked_minutes,
        "total_overtime_minutes": total_overtime_minutes,
    }

    return render(
        request,
        "attendance/departments.html",
        context,
    )
 
def get_attendance_report_data(request):
    """
    Build the attendance report using the filters supplied
    through the request.
    """

    today = timezone.localdate()

    # ==========================================================
    # FILTER VALUES
    # ==========================================================

    date_from_param = request.GET.get("date_from", "").strip()
    date_to_param = request.GET.get("date_to", "").strip()

    employee_search = request.GET.get("employee", "").strip()
    department_filter = request.GET.get("department", "").strip()
    status_filter = request.GET.get("status", "").strip().lower()

    # ==========================================================
    # DATE RANGE
    # ==========================================================

    date_from = (
        parse_date(date_from_param)
        if date_from_param
        else today
    )

    date_to = (
        parse_date(date_to_param)
        if date_to_param
        else today
    )

    if not date_from:
        date_from = today

    if not date_to:
        date_to = today

    if date_from > date_to:
        date_from, date_to = date_to, date_from

    # ==========================================================
    # EMPLOYEES
    # ==========================================================

    employees = (
        Employee.objects
        .select_related("department")
        .all()
        .order_by(
            "first_name",
            "middle_name",
            "last_name",
        )
    )

    if employee_search:

        search_q = (
            Q(employee_number__icontains=employee_search)
            | Q(first_name__icontains=employee_search)
            | Q(middle_name__icontains=employee_search)
            | Q(last_name__icontains=employee_search)
        )

        # employee_id is an integer
        if employee_search.isdigit():
            search_q |= Q(
                employee_id=int(employee_search)
            )

        employees = employees.filter(search_q)

    # ==========================================================
    # DEPARTMENT FILTER
    # ==========================================================

    if department_filter:
        employees = employees.filter(
            department_id=department_filter
        )

    employee_ids = list(
        employees.values_list(
            "id",
            flat=True,
        )
    )

    # ==========================================================
    # ATTENDANCE
    # ==========================================================

    attendance_records = (
        Attendance.objects
        .filter(
            attendance_date__range=(
                date_from,
                date_to,
            ),
            employee_id__in=employee_ids,
        )
        .select_related(
            "employee",
            "employee__department",
        )
        .order_by(
            "attendance_date",
            "employee__first_name",
            "employee__middle_name",
            "employee__last_name",
        )
    )

    if status_filter:
        attendance_records = attendance_records.filter(
            status__iexact=status_filter
        )

    # ==========================================================
    # REPORT ROWS
    # ==========================================================

    report_rows = []

    for record in attendance_records:

        employee = record.employee

        employee_name = " ".join(
            part
            for part in [
                employee.first_name,
                employee.middle_name,
                employee.last_name,
            ]
            if part
        )

        department_name = ""

        if employee.department:
            department_name = employee.department.name

        report_rows.append({
            "record": record,
            "employee": employee,
            "employee_name": employee_name,
            "department_name": department_name,
            "worked_minutes": record.worked_minutes or 0,
            "overtime_minutes": record.overtime_minutes or 0,
            "late_minutes": record.late_minutes or 0,
            "early_leave_minutes": (
                record.early_leave_minutes or 0
            ),
        })

    # ==========================================================
    # SUMMARY
    # ==========================================================

    total_records = len(report_rows)

    total_present = 0
    total_late = 0
    total_absent = 0
    total_leave = 0

    total_worked_minutes = 0
    total_overtime_minutes = 0
    total_late_minutes = 0
    total_early_leave_minutes = 0

    for row in report_rows:

        status = (
            row["record"].status or ""
        ).lower()

        if status == "present":
            total_present += 1

        elif status == "late":
            total_late += 1

        elif status == "absent":
            total_absent += 1

        elif status == "leave":
            total_leave += 1

        total_worked_minutes += row["worked_minutes"]
        total_overtime_minutes += row["overtime_minutes"]
        total_late_minutes += row["late_minutes"]
        total_early_leave_minutes += (
            row["early_leave_minutes"]
        )

    attended_records = (
        total_present + total_late
    )

    attendance_rate = 0

    if total_records:
        attendance_rate = round(
            (attended_records / total_records) * 100,
            1,
        )

    total_worked_hours = round(
        total_worked_minutes / 60,
        2,
    )

    total_overtime_hours = round(
        total_overtime_minutes / 60,
        2,
    )

    return {
        "report_rows": report_rows,

        "date_from": date_from,
        "date_to": date_to,

        "employee_search": employee_search,
        "department_filter": department_filter,
        "status_filter": status_filter,

        "total_records": total_records,
        "total_present": total_present,
        "total_late": total_late,
        "total_absent": total_absent,
        "total_leave": total_leave,

        "attendance_rate": attendance_rate,

        "total_worked_minutes": total_worked_minutes,
        "total_overtime_minutes": total_overtime_minutes,

        "total_worked_hours": total_worked_hours,
        "total_overtime_hours": total_overtime_hours,

        "total_late_minutes": total_late_minutes,
        "total_early_leave_minutes": total_early_leave_minutes,
    } 


@login_required
def attendance_reports(request):

    data = get_attendance_report_data(request)

    departments = (
        Employee.objects
        .filter(
            department__isnull=False
        )
        .values(
            "department_id",
            "department__name",
        )
        .distinct()
        .order_by(
            "department__name"
        )
    )

    data["departments"] = departments

    return render(
        request,
        "attendance/reports.html",
        data,
    )
 
 
 
@login_required
def attendance_report_pdf(request):

    data = get_attendance_report_data(request)

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=16,
        leading=20,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        leading=14,
    )

    story = []

    # ==========================================================
    # TITLE
    # ==========================================================

    story.append(
        Paragraph(
            "SMART ACCESS CONTROL SYSTEM",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Attendance Report",
            styles["Heading2"],
        )
    )

    story.append(
        Paragraph(
            f"Period: "
            f"{data['date_from'].strftime('%d %b %Y')} "
            f"to "
            f"{data['date_to'].strftime('%d %b %Y')}",
            subtitle_style,
        )
    )

    story.append(
        Spacer(1, 8)
    )

    # ==========================================================
    # SUMMARY
    # ==========================================================

    summary_data = [
        [
            "Records",
            "Present",
            "Late",
            "Absent",
            "Leave",
            "Attendance Rate",
        ],
        [
            str(data["total_records"]),
            str(data["total_present"]),
            str(data["total_late"]),
            str(data["total_absent"]),
            str(data["total_leave"]),
            f"{data['attendance_rate']}%",
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            35 * mm,
            30 * mm,
            30 * mm,
            30 * mm,
            30 * mm,
            40 * mm,
        ],
    )

    summary_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#D9EAF7"),
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER",
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
        ])
    )

    story.append(summary_table)

    story.append(
        Spacer(1, 10)
    )

    # ==========================================================
    # REPORT TABLE
    # ==========================================================

    table_data = [[
        "#",
        "Employee",
        "ID",
        "Department",
        "Date",
        "Check In",
        "Check Out",
        "Late",
        "Early",
        "Worked",
        "OT",
        "Status",
    ]]

    for index, row in enumerate(
        data["report_rows"],
        start=1,
    ):

        record = row["record"]

        table_data.append([
            str(index),
            row["employee_name"],
            str(row["employee"].employee_id),
            row["department_name"] or "-",
            record.attendance_date.strftime(
                "%d %b %Y"
            ),
            (
                record.check_in.strftime("%H:%M")
                if record.check_in
                else "-"
            ),
            (
                record.check_out.strftime("%H:%M")
                if record.check_out
                else "-"
            ),
            str(row["late_minutes"]),
            str(row["early_leave_minutes"]),
            str(row["worked_minutes"]),
            str(row["overtime_minutes"]),
            str(record.status or ""),
        ])

    report_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            8 * mm,
            38 * mm,
            20 * mm,
            35 * mm,
            25 * mm,
            18 * mm,
            18 * mm,
            15 * mm,
            15 * mm,
            18 * mm,
            15 * mm,
            20 * mm,
        ],
    )

    report_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#D9EAF7"),
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7,
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER",
            ),
            (
                "ALIGN",
                (1, 1),
                (1, -1),
                "LEFT",
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.grey,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                4,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                4,
            ),
        ])
    )

    story.append(report_table)

    story.append(
        Spacer(1, 10)
    )

    story.append(
        Paragraph(
            f"Total Worked Hours: "
            f"{data['total_worked_hours']} | "
            f"Total Overtime Hours: "
            f"{data['total_overtime_hours']}",
            subtitle_style,
        )
    )

    # ==========================================================
    # BUILD PDF
    # ==========================================================

    document.build(story)

    buffer.seek(0)

    filename = (
        "attendance_report_"
        f"{data['date_from'].strftime('%Y%m%d')}_"
        f"{data['date_to'].strftime('%Y%m%d')}.pdf"
    )

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf",
    )

    response[
        "Content-Disposition"
    ] = f'attachment; filename="{filename}"'

    return response
    
    
@login_required
def attendance_report_excel(request):

    data = get_attendance_report_data(request)

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Attendance Report"

    # ==========================================================
    # TITLE
    # ==========================================================

    worksheet.merge_cells("A1:L1")
    worksheet["A1"] = "SMART ACCESS CONTROL SYSTEM"

    worksheet["A1"].font = Font(
        bold=True,
        size=16,
    )

    worksheet["A1"].alignment = Alignment(
        horizontal="center"
    )

    worksheet.merge_cells("A2:L2")
    worksheet["A2"] = "Attendance Report"

    worksheet["A2"].font = Font(
        bold=True,
        size=13,
    )

    worksheet["A2"].alignment = Alignment(
        horizontal="center"
    )

    worksheet.merge_cells("A3:L3")
    worksheet["A3"] = (
        f"Period: "
        f"{data['date_from'].strftime('%d %b %Y')} "
        f"to "
        f"{data['date_to'].strftime('%d %b %Y')}"
    )

    worksheet["A3"].alignment = Alignment(
        horizontal="center"
    )

    # ==========================================================
    # SUMMARY
    # ==========================================================

    summary = [
        ("Total Records", data["total_records"]),
        ("Present", data["total_present"]),
        ("Late", data["total_late"]),
        ("Absent", data["total_absent"]),
        ("Leave", data["total_leave"]),
        ("Attendance Rate", f"{data['attendance_rate']}%"),
    ]

    for index, (label, value) in enumerate(summary):

        column = index * 2 + 1

        worksheet.cell(
            row=5,
            column=column,
            value=label,
        ).font = Font(bold=True)

        worksheet.cell(
            row=5,
            column=column + 1,
            value=value,
        ).font = Font(bold=True)

    # ==========================================================
    # TABLE HEADER
    # ==========================================================

    header_row = 7

    headers = [
        "#",
        "Employee",
        "Employee ID",
        "Department",
        "Date",
        "Check In",
        "Check Out",
        "Late (min)",
        "Early Leave (min)",
        "Worked (min)",
        "Overtime (min)",
        "Status",
    ]

    for column, header in enumerate(headers, start=1):

        cell = worksheet.cell(
            row=header_row,
            column=column,
            value=header,
        )

        cell.font = Font(bold=True)

        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
        )

        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="D9EAF7",
        )

    # ==========================================================
    # DATA
    # ==========================================================

    row_number = header_row + 1

    for index, row in enumerate(
        data["report_rows"],
        start=1,
    ):

        record = row["record"]

        values = [
            index,
            row["employee_name"],
            row["employee"].employee_id,
            row["department_name"],
            record.attendance_date,
            (
                record.check_in.strftime("%H:%M")
                if record.check_in
                else ""
            ),
            (
                record.check_out.strftime("%H:%M")
                if record.check_out
                else ""
            ),
            row["late_minutes"],
            row["early_leave_minutes"],
            row["worked_minutes"],
            row["overtime_minutes"],
            record.status or "",
        ]

        for column, value in enumerate(
            values,
            start=1,
        ):

            worksheet.cell(
                row=row_number,
                column=column,
                value=value,
            )

        row_number += 1

    # ==========================================================
    # BORDERS
    # ==========================================================

    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    for row in worksheet.iter_rows(
        min_row=header_row,
        max_row=max(row_number - 1, header_row),
        min_col=1,
        max_col=12,
    ):

        for cell in row:

            cell.border = thin_border

            cell.alignment = Alignment(
                vertical="center"
            )

    # ==========================================================
    # DATE FORMAT
    # ==========================================================

    for row in range(
        header_row + 1,
        row_number,
    ):

        worksheet.cell(
            row=row,
            column=5,
        ).number_format = "dd mmm yyyy"

    # ==========================================================
    # COLUMN WIDTHS
    # ==========================================================

    widths = [
        6,
        28,
        14,
        22,
        15,
        12,
        12,
        12,
        18,
        15,
        17,
        14,
    ]

    for index, width in enumerate(
        widths,
        start=1,
    ):

        worksheet.column_dimensions[
            get_column_letter(index)
        ].width = width

    worksheet.freeze_panes = "A8"

    # ==========================================================
    # DOWNLOAD
    # ==========================================================

    output = io.BytesIO()

    workbook.save(output)

    output.seek(0)

    filename = (
        "attendance_report_"
        f"{data['date_from'].strftime('%Y%m%d')}_"
        f"{data['date_to'].strftime('%Y%m%d')}.xlsx"
    )

    response = HttpResponse(
        output.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    return response