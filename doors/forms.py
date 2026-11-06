from django import forms

from .models import Door


class DoorForm(forms.ModelForm):

    class Meta:
        model = Door

        fields = [
            "door_code",
            "name",
            "location",
            "lock_type",
            "unlock_duration_seconds",
            "sensor_enabled",
            "exit_button_enabled",
            "is_active",
        ]

        widgets = {
            "door_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: D001",
                }
            ),

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: Main Entrance",
                }
            ),

            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: Main Building",
                }
            ),

            "lock_type": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: Electric Lock",
                }
            ),

            "unlock_duration_seconds": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),

            "sensor_enabled": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "exit_button_enabled": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }