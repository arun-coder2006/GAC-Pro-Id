from django import forms
from .models import Student


class StudentForm(forms.ModelForm):

    class Meta:
        model = Student

        fields = [
            "name",
            "to_place",
            "roll_no",
            "photo",
        ]

        labels = {
            "name": "Name",
            "to_place": "To",
            "roll_no": "Roll No (Optional)",
            "photo": "Photo",
        }

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Enter your name"
                }
            ),

            "to_place": forms.TextInput(
                attrs={
                    "placeholder": "Enter destination"
                }
            ),

            "roll_no": forms.TextInput(
                attrs={
                    "placeholder": "Enter roll number (optional)"
                }
            ),

            "photo": forms.ClearableFileInput(
                attrs={
                    "accept": ".jpg,.jpeg,.png"
                }
            ),
        }

    def clean_photo(self):

        photo = self.cleaned_data.get("photo")

        if not photo:
            raise forms.ValidationError(
                "Please upload your photo."
            )

        max_size = 2 * 1024 * 1024

        if photo.size > max_size:

            raise forms.ValidationError(
                "Photo size must not exceed 2 MB."
            )

        filename = photo.name.lower()

        allowed_extensions = (
            ".jpg",
            ".jpeg",
            ".png"
        )

        if not filename.endswith(
            allowed_extensions
        ):

            raise forms.ValidationError(
                "Only JPG, JPEG and PNG images are allowed."
            )

        return photo


# ============================================================
# STAFF EDIT FORM
# ============================================================

class StaffStudentEditForm(forms.ModelForm):

    class Meta:
        model = Student

        fields = [
            "name",
            "to_place",
            "roll_no",
            "photo",
            "is_leader",
        ]

        labels = {
            "name": "Name",
            "to_place": "To",
            "roll_no": "Roll No",
            "photo": "Photo",
            "is_leader": "Make Representative",
        }

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Enter student name"
                }
            ),

            "to_place": forms.TextInput(
                attrs={
                    "placeholder": "Enter destination"
                }
            ),

            "roll_no": forms.TextInput(
                attrs={
                    "placeholder": "Enter roll number"
                }
            ),

            "photo": forms.ClearableFileInput(
                attrs={
                    "accept": ".jpg,.jpeg,.png"
                }
            ),

            "is_leader": forms.CheckboxInput(),
        }

    def clean_photo(self):

        photo = self.cleaned_data.get("photo")

        # Photo is optional during editing.
        # Existing photo will remain if no new photo is selected.

        if not photo:
            return photo

        max_size = 2 * 1024 * 1024

        if photo.size > max_size:

            raise forms.ValidationError(
                "Photo size must not exceed 2 MB."
            )

        filename = photo.name.lower()

        allowed_extensions = (
            ".jpg",
            ".jpeg",
            ".png"
        )

        if not filename.endswith(
            allowed_extensions
        ):

            raise forms.ValidationError(
                "Only JPG, JPEG and PNG images are allowed."
            )

        return photo