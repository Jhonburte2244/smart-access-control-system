
from django import forms

from employees.models import Employee, FaceTemplate


class FaceEnrollmentForm(forms.Form):

    # ========================================================
    # EMPLOYEE
    # ========================================================

    employee = forms.ModelChoiceField(
        queryset=Employee.objects.none(),
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        empty_label="Select employee",
    )

    # ========================================================
    # FACE IMAGE
    # ========================================================

    image = forms.ImageField(
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": "image/*",
            }
        ),
        help_text=(
            "Upload a clear image containing exactly one face."
        ),
    )

    # ========================================================
    # ALGORITHM
    # ========================================================

    algorithm = forms.CharField(
        initial="OpenCV YuNet + SFace",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "readonly": "readonly",
            }
        ),
    )

    # ========================================================
    # CONFIDENCE THRESHOLD
    # ========================================================

    confidence_threshold = forms.DecimalField(
        initial=80.00,
        min_value=0,
        max_value=100,
        decimal_places=2,
        max_digits=5,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "max": "100",
            }
        ),
    )

    # ========================================================
    # INITIALIZE
    # ========================================================

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields[
            "employee"
        ].queryset = (
            Employee.objects
            .all()
            .order_by("employee_number")
        )

    # ========================================================
    # CHECK DUPLICATE ACTIVE TEMPLATE
    # ========================================================

    def clean_employee(self):

        employee = self.cleaned_data["employee"]

        existing_template = (
            FaceTemplate.objects
            .filter(
                employee=employee,
                status="active",
            )
            .first()
        )

        if existing_template:

            raise forms.ValidationError(
                "This employee already has an active "
                "face template. Edit or deactivate the "
                "existing template before enrolling another face."
            )

        return employee

    # ========================================================
    # CHECK IMAGE
    # ========================================================

    def clean_image(self):

        image = self.cleaned_data["image"]

        # Basic file-size protection
        max_size = 10 * 1024 * 1024

        if image.size > max_size:

            raise forms.ValidationError(
                "Image size must not exceed 10 MB."
            )

        # Make sure Django identified it as an image
        if not image.content_type.startswith("image/"):

            raise forms.ValidationError(
                "Please upload a valid image file."
            )

        return image


# ============================================================
# FACE TEMPLATE EDIT FORM
# ============================================================

class FaceTemplateForm(forms.ModelForm):

    class Meta:

        model = FaceTemplate

        fields = [
            "employee",
            "algorithm",
            "confidence_threshold",
            "status",
        ]

        widgets = {

            "employee": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "algorithm": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                }
            ),

            "confidence_threshold": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields[
            "employee"
        ].queryset = (
            Employee.objects
            .all()
            .order_by("employee_number")
        )
