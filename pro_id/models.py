from django.db import models


class Department(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    class_name = models.CharField(
        max_length=150
    )

    admin_password = models.CharField(
        max_length=128
    )

    def __str__(self):
        return self.name


class Student(models.Model):

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="students"
    )

    student_key = models.CharField(
        max_length=100,
        unique=True
    )

    name = models.CharField(
        max_length=150
    )

    to_place = models.CharField(
        max_length=150
    )

    roll_no = models.CharField(
        max_length=50,
        blank=True
    )

    photo = models.ImageField(
        upload_to="student_photos/"
    )

    submission_year = models.PositiveIntegerField(
        default=2026
    )

    is_leader = models.BooleanField(
        default=False
    )

    pdf_generated = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name