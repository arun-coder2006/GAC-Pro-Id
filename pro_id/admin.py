from django.contrib import admin
from .models import Department, Student


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "class_name")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "student_key",
        "department",
        "roll_no",
        "is_leader",
        "pdf_generated",
    )

    list_filter = (
        "department",
        "is_leader",
        "pdf_generated",
    )

    search_fields = (
        "name",
        "student_key",
    )