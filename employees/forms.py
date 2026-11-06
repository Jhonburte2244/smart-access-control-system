from django import forms

from .models import Employee


class EmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee

        fields = [
            "employee_number",
            "first_name",
            "middle_name",
            "last_name",
            "gender",
            "date_of_birth",
            "phone",
            "email",
            "address",
            "job_title",
            "department_id",
            "hire_date",
            "photo_path",
            "status",
        ]

        widgets = {

            "employee_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "EMP002",
                }
            ),

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "First name",
                }
            ),

            "middle_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Middle name",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Last name",
                }
            ),

            "gender": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Male / Female",
                }
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0911000000",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "employee@example.com",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Address",
                }
            ),

            "job_title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Security Officer",
                }
            ),

            "department_id": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Department ID",
                }
            ),

            "hire_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "photo_path": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Photo path",
                }
            ),

            "status": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "active",
                }
            ),
        }