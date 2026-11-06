
from django.utils import timezone
from access_control.models import DoorPermission
from employees.models import Employee
from django.db import models
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from doors.models import Door


class AccessDecisionService:
    """
    Central authorization engine for the Smart Access Control System.

    This service checks whether an employee is allowed to access
    a specific door at the current date and time.

    It does NOT unlock the door and does NOT create access logs.
    Those will be handled by the next integration layer.
    """

    WEEKDAY_FIELDS = {
        0: "monday",
        1: "tuesday",
        2: "wednesday",
        3: "thursday",
        4: "friday",
        5: "saturday",
        6: "sunday",
    }

    @classmethod
    def check_access(cls, employee, door, check_time=None):
        """
        Check whether an employee can access a door.

        Returns:

        {
            "granted": True/False,
            "employee": employee,
            "door": door,
            "permission": permission,
            "access_rule": access_rule,
            "reason": "...",
        }
        """

        # --------------------------------------------------
        # 1. Validate employee
        # --------------------------------------------------
        if not employee:
            return cls._deny(
                employee=None,
                door=door,
                reason="Employee not found.",
            )

        # --------------------------------------------------
        # 2. Check employee status
        # --------------------------------------------------
        if str(employee.status).lower() != "active":
            return cls._deny(
                employee=employee,
                door=door,
                reason="Employee account is not active.",
            )

        # --------------------------------------------------
        # 3. Validate door
        # --------------------------------------------------
        if not door:
            return cls._deny(
                employee=employee,
                door=None,
                reason="Door not found.",
            )

        # --------------------------------------------------
        # 4. Check door status
        # --------------------------------------------------
        if not door.is_active:
            return cls._deny(
                employee=employee,
                door=door,
                reason="Door is not active.",
            )

        # --------------------------------------------------
        # 5. Get current date/time
        # --------------------------------------------------
        if check_time is None:
            check_time = timezone.localtime()

        current_date = check_time.date()
        current_time = check_time.time()

        # --------------------------------------------------
        # 6. Find active employee permission for this door
        # --------------------------------------------------
        permission = (
            DoorPermission.objects
            .select_related("door", "employee", "role", "access_rule")
            .filter(
                door=door,
                employee=employee,
                is_active=True,
            )
            .first()
        )

        if not permission:
            return cls._deny(
                employee=employee,
                door=door,
                reason="Employee does not have permission for this door.",
            )

        # --------------------------------------------------
        # 7. Get access rule
        # --------------------------------------------------
        access_rule = permission.access_rule

        if not access_rule:
            return cls._deny(
                employee=employee,
                door=door,
                permission=permission,
                reason="No access rule is assigned to this permission.",
            )

        # --------------------------------------------------
        # 8. Check access rule status
        # --------------------------------------------------
        if not access_rule.is_active:
            return cls._deny(
                employee=employee,
                door=door,
                permission=permission,
                access_rule=access_rule,
                reason="Access rule is inactive.",
            )

        # --------------------------------------------------
        # 9. Check valid-from date
        # --------------------------------------------------
        if (
            access_rule.valid_from
            and current_date < access_rule.valid_from
        ):
            return cls._deny(
                employee=employee,
                door=door,
                permission=permission,
                access_rule=access_rule,
                reason="Access rule is not yet valid.",
            )

        # --------------------------------------------------
        # 10. Check valid-until date
        # --------------------------------------------------
        if (
            access_rule.valid_until
            and current_date > access_rule.valid_until
        ):
            return cls._deny(
                employee=employee,
                door=door,
                permission=permission,
                access_rule=access_rule,
                reason="Access rule has expired.",
            )

        # --------------------------------------------------
        # 11. Check weekday
        # --------------------------------------------------
        weekday_field = cls.WEEKDAY_FIELDS.get(
            check_time.weekday()
        )

        if weekday_field and not getattr(
            access_rule,
            weekday_field,
            False,
        ):
            return cls._deny(
                employee=employee,
                door=door,
                permission=permission,
                access_rule=access_rule,
                reason="Access is not allowed on this day.",
            )

        # --------------------------------------------------
        # 12. Check time range
        # --------------------------------------------------
        start_time = access_rule.start_time
        end_time = access_rule.end_time

        if start_time and end_time:

            # Normal period, e.g. 08:00 → 17:00
            if start_time <= end_time:

                if not (
                    start_time <= current_time <= end_time
                ):
                    return cls._deny(
                        employee=employee,
                        door=door,
                        permission=permission,
                        access_rule=access_rule,
                        reason="Access is outside the allowed time.",
                    )

            # Overnight period, e.g. 22:00 → 06:00
            else:

                if not (
                    current_time >= start_time
                    or current_time <= end_time
                ):
                    return cls._deny(
                        employee=employee,
                        door=door,
                        permission=permission,
                        access_rule=access_rule,
                        reason="Access is outside the allowed time.",
                    )

        # --------------------------------------------------
        # 13. Access granted
        # --------------------------------------------------
        return {
            "granted": True,
            "employee": employee,
            "door": door,
            "permission": permission,
            "access_rule": access_rule,
            "reason": "Access granted.",
        }

    # ======================================================
    # DENY HELPER
    # ======================================================

    @staticmethod
    def _deny(
        employee=None,
        door=None,
        permission=None,
        access_rule=None,
        reason="Access denied.",
    ):
        return {
            "granted": False,
            "employee": employee,
            "door": door,
            "permission": permission,
            "access_rule": access_rule,
            "reason": reason,
        }
