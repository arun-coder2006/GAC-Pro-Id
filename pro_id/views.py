from django.contrib import messages
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from io import BytesIO
from django.db import transaction
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from PIL import Image as PILImage
from .pdf_generator import generate_pdf
from django.http import FileResponse
from django.contrib.auth.hashers import check_password

import os
from django.db.models import Count
from django.utils import timezone

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import Department, Student
#from .forms import StudentForm
from .forms import (
    StudentForm,
    StaffStudentEditForm
)


# ============================================================
# HOME
# ============================================================
def welcome(request):
    return render(request, "welcome.html")

def home(request):

    departments = Department.objects.all()

    return render(
        request,
        "home.html",
        {
            "departments": departments
        }
    )
def department_options(request, department_id):

    department = get_object_or_404(
        Department,
        id=department_id
    )

    return render(
        request,
        "department_options.html",
        {
            "department": department
        }
    )
def admin_department_select(request):
    departments = Department.objects.all()

    return render(
        request,
        "admin_department_select.html",
        {
            "departments": departments
        }
    )
def department_options(request, department_id):

    department = get_object_or_404(
        Department,
        id=department_id
    )

    return render(
        request,
        "department_options.html",
        {
            "department": department
        }
    )

# ============================================================
# STUDENT LOGIN
# ============================================================
def student_login(request, department_id):

    department = get_object_or_404(
        Department,
        id=department_id
    )

    error = None

    if request.method == "POST":

        student_key = request.POST.get(
            "student_key",
            ""
        ).strip()

        if not student_key:

            error = (
                "Please enter your application "
                "number or password."
            )

            return render(
                request,
                "student_login.html",
                {
                    "department": department,
                    "error": error,
                }
            )

        try:

            student = Student.objects.get(
                student_key=student_key
            )

            if student.department_id != department.id:

                error = (
                    "This application number/password "
                    "belongs to another department."
                )

                return render(
                    request,
                    "student_login.html",
                    {
                        "department": department,
                        "error": error,
                    }
                )

            request.session["student_id"] = student.id

            request.session.pop(
                "department_id",
                None
            )

            request.session.pop(
                "student_key",
                None
            )

            request.session.pop(
                "preview_name",
                None
            )

            request.session.pop(
                "preview_to",
                None
            )

            request.session.pop(
                "preview_roll_no",
                None
            )

            request.session.pop(
                "preview_photo",
                None
            )

            return redirect(
                "student_status"
            )

        except Student.DoesNotExist:

            request.session["department_id"] = (
                department.id
            )

            request.session["student_key"] = (
                student_key
            )

            request.session.pop(
                "student_id",
                None
            )

            request.session.pop(
                "preview_name",
                None
            )

            request.session.pop(
                "preview_to",
                None
            )

            request.session.pop(
                "preview_roll_no",
                None
            )

            request.session.pop(
                "preview_photo",
                None
            )

            return redirect(
                "student_form"
            )

    return render(
        request,
        "student_login.html",
        {
            "department": department,
            "error": error,
        }
    )

# ============================================================
# STUDENT FORM
# ============================================================

def student_form(request):

    # --------------------------------------------------------
    # FIRST: CHECK WHETHER THIS STUDENT ALREADY SUBMITTED
    # --------------------------------------------------------

    student_id = request.session.get(
        "student_id"
    )

    if student_id:

        student = get_object_or_404(
            Student,
            id=student_id
        )

        # IMPORTANT:
        # An already submitted student must NEVER see
        # the form again.

        return redirect(
            "student_status"
        )

    # --------------------------------------------------------
    # GET NEW STUDENT SESSION INFORMATION
    # --------------------------------------------------------

    department_id = request.session.get(
        "department_id"
    )

    student_key = request.session.get(
        "student_key"
    )

    if not department_id or not student_key:

        return redirect(
            "home"
        )

    department = get_object_or_404(
        Department,
        id=department_id
    )

    # --------------------------------------------------------
    # FORM SUBMISSION
    # --------------------------------------------------------

    if request.method == "POST":

        form = StudentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            # ----------------------------------------------
            # DOUBLE CHECK DATABASE
            # ----------------------------------------------

            existing_student = Student.objects.filter(
                student_key=student_key
            ).first()

            if existing_student:

                # ------------------------------------------
                # DIFFERENT DEPARTMENT
                # ------------------------------------------

                if existing_student.department_id != department.id:

                    messages.error(
                        request,
                        "This application number/password belongs to another department."
                    )

                    return redirect(
                        "home"
                    )

                # ------------------------------------------
                # SAME DEPARTMENT
                # ------------------------------------------

                request.session["student_id"] = (
                    existing_student.id
                )

                return redirect(
                    "student_status"
                )

            # ----------------------------------------------
            # SAVE PREVIEW DATA
            # ----------------------------------------------

            request.session["preview_name"] = (
                form.cleaned_data["name"]
            )

            request.session["preview_to"] = (
                form.cleaned_data["to_place"]
            )

            request.session["preview_roll_no"] = (
                form.cleaned_data["roll_no"]
            )

            # ----------------------------------------------
            # SAVE PHOTO TEMPORARILY
            # ----------------------------------------------

            photo = form.cleaned_data["photo"]

            temp_path = (
                "temp_student_photos/"
                + photo.name
            )

            saved_path = default_storage.save(
                temp_path,
                ContentFile(
                    photo.read()
                )
            )

            request.session["preview_photo"] = (
                saved_path
            )

            # ----------------------------------------------
            # GO TO PREVIEW
            # ----------------------------------------------

            return redirect(
                "student_preview"
            )

    else:

        form = StudentForm(
        initial={
            "name": request.session.get("preview_name", ""),
            "to_place": request.session.get("preview_to", ""),
            "roll_no": request.session.get("preview_roll_no", ""),
        }
    )

    return render(
        request,
        "student_form.html",
        {
            "form": form,
            "department": department,
        }
    )


# ============================================================
# STUDENT PREVIEW
# ============================================================

def student_preview(request):

    # --------------------------------------------------------
    # CHECK WHETHER ALREADY SUBMITTED
    # --------------------------------------------------------

    student_id = request.session.get(
        "student_id"
    )

    if student_id:

        return redirect(
            "student_status"
        )

    # --------------------------------------------------------
    # GET NEW STUDENT SESSION DATA
    # --------------------------------------------------------

    department_id = request.session.get(
        "department_id"
    )

    student_key = request.session.get(
        "student_key"
    )

    if not department_id or not student_key:

        return redirect(
            "home"
        )

    # --------------------------------------------------------
    # DOUBLE CHECK DATABASE
    # --------------------------------------------------------

    existing_student = Student.objects.filter(
        student_key=student_key
    ).first()

    if existing_student:

        request.session["student_id"] = (
            existing_student.id
        )

        return redirect(
            "student_status"
        )

    department = get_object_or_404(
        Department,
        id=department_id
    )

    # --------------------------------------------------------
    # GET PREVIEW DATA
    # --------------------------------------------------------

    name = request.session.get(
        "preview_name"
    )

    to_place = request.session.get(
        "preview_to"
    )

    roll_no = request.session.get(
        "preview_roll_no"
    )

    photo = request.session.get(
        "preview_photo"
    )

    # --------------------------------------------------------
    # CHECK PREVIEW DATA
    # --------------------------------------------------------

    if not name or not to_place or not photo:

        return redirect(
            "student_form"
        )

    # --------------------------------------------------------
    # DISPLAY PREVIEW
    # --------------------------------------------------------

    return render(
        request,
        "student_preview.html",
        {
            "department": department,
            "name": name,
            "to_place": to_place,
            "roll_no": roll_no,
            "photo": photo,
        }
    )


# ============================================================
# STUDENT CONFIRM
# ============================================================

# ============================================================
# STUDENT CONFIRM
# ============================================================

def student_confirm(request):

    # --------------------------------------------------------
    # ONLY POST IS ALLOWED
    # --------------------------------------------------------

    if request.method != "POST":

        return redirect(
            "student_form"
        )

    # --------------------------------------------------------
    # CHECK WHETHER ALREADY SAVED
    # --------------------------------------------------------

    existing_student_id = request.session.get(
        "student_id"
    )

    if existing_student_id:

        return redirect(
            "student_status"
        )

    # --------------------------------------------------------
    # GET SESSION DATA
    # --------------------------------------------------------

    department_id = request.session.get(
        "department_id"
    )

    student_key = request.session.get(
        "student_key"
    )

    name = request.session.get(
        "preview_name"
    )

    to_place = request.session.get(
        "preview_to"
    )

    roll_no = request.session.get(
        "preview_roll_no"
    )

    temp_photo = request.session.get(
        "preview_photo"
    )

    # --------------------------------------------------------
    # CHECK TEMPORARY DATA
    # --------------------------------------------------------

    if not all([
        department_id,
        student_key,
        name,
        to_place,
        temp_photo
    ]):

        return redirect(
            "student_form"
        )

    # --------------------------------------------------------
    # GET DEPARTMENT
    # --------------------------------------------------------

    department = get_object_or_404(
        Department,
        id=department_id
    )

    # --------------------------------------------------------
    # FINAL DATABASE DUPLICATE CHECK
    # --------------------------------------------------------

    existing_student = Student.objects.filter(
        student_key=student_key
    ).first()

    if existing_student:

        # ----------------------------------------------------
        # WRONG DEPARTMENT
        # ----------------------------------------------------

        if existing_student.department_id != department.id:

            messages.error(
                request,
                "This application number/password belongs to another department."
            )

            return redirect(
                "home"
            )

        # ----------------------------------------------------
        # SAME STUDENT
        # ----------------------------------------------------

        request.session["student_id"] = (
            existing_student.id
        )

        # Delete unused temporary photo
        if default_storage.exists(temp_photo):

            default_storage.delete(
                temp_photo
            )

        return redirect(
            "student_status"
        )

    # --------------------------------------------------------
    # CREATE STUDENT
    # --------------------------------------------------------

    student = Student(
        department=department,
        student_key=student_key,
        name=name,
        to_place=to_place,
        roll_no=roll_no,
    )

    # --------------------------------------------------------
    # SAVE STUDENT PHOTO PERMANENTLY
    # --------------------------------------------------------

    try:

        if not default_storage.exists(
            temp_photo
        ):

            messages.error(
                request,
                "The uploaded photo could not be found. Please upload it again."
            )

            return redirect(
                "student_form"
            )

        with default_storage.open(
            temp_photo,
            "rb"
        ) as photo_file:

            photo_data = photo_file.read()

        original_name = os.path.basename(
            temp_photo
        )

        student.photo.save(
            original_name,
            ContentFile(photo_data),
            save=False
        )

        # ----------------------------------------------------
        # SAVE STUDENT
        # ----------------------------------------------------

        student.save()

    finally:

        # ----------------------------------------------------
        # REMOVE TEMPORARY PHOTO
        # ----------------------------------------------------

        if default_storage.exists(
            temp_photo
        ):

            default_storage.delete(
                temp_photo
            )

    # --------------------------------------------------------
    # SAVE STUDENT ID IN SESSION
    # --------------------------------------------------------

    request.session["student_id"] = (
        student.id
    )

    # --------------------------------------------------------
    # CLEAR SESSION DATA
    # --------------------------------------------------------

    request.session.pop(
        "department_id",
        None
    )

    request.session.pop(
        "student_key",
        None
    )

    request.session.pop(
        "preview_name",
        None
    )

    request.session.pop(
        "preview_to",
        None
    )

    request.session.pop(
        "preview_roll_no",
        None
    )

    request.session.pop(
        "preview_photo",
        None
    )

    # --------------------------------------------------------
    # SUCCESS PAGE
    # --------------------------------------------------------

    return render(
        request,
        "student_success.html",
        {
            "student": student,
            "department": department,
        }
    )
# ============================================================
# STUDENT STATUS
# ============================================================

def student_status(request):

    # --------------------------------------------------------
    # GET SAVED STUDENT ID
    # --------------------------------------------------------

    student_id = request.session.get(
        "student_id"
    )

    if not student_id:

        return redirect(
            "home"
        )

    # --------------------------------------------------------
    # GET STUDENT
    # --------------------------------------------------------

    student = get_object_or_404(
        Student,
        id=student_id
    )

    # --------------------------------------------------------
    # SHOW STATUS
    # --------------------------------------------------------

    return render(
        request,
        "student_status.html",
        {
            "student": student,
            "department": student.department,
        }
    )
from django.contrib.auth.hashers import check_password


from django.contrib.auth.hashers import check_password


# ============================================================
# ADMIN LOGIN
# ============================================================

# ============================================================
# STAFF LOGIN
# ============================================================

def admin_login(request, department_id):

    department = get_object_or_404(
        Department,
        id=department_id
    )

    error = None

    if request.method == "POST":

        password = request.POST.get(
            "password",
            ""
        ).strip()

        if not check_password(
            password,
            department.admin_password
        ):

            error = "Invalid staff password."

        else:

            request.session["admin_department_id"] = (
                department.id
            )

            request.session["admin_logged_in"] = True

            return redirect(
                "admin_dashboard"
            )

    return render(
        request,
        "admin_login.html",
        {
            "department": department,
            "error": error,
        }
    )
def admin_department_select(request):

    departments = Department.objects.all()

    return render(
        request,
        "admin_department_select.html",
        {
            "departments": departments
        }
    )

def admin_dashboard(request):

    # --------------------------------------------------------
    # CHECK STAFF LOGIN
    # --------------------------------------------------------

    if not request.session.get("admin_logged_in"):

        return redirect("home")


    # --------------------------------------------------------
    # GET STAFF DEPARTMENT
    # --------------------------------------------------------

    department_id = request.session.get(
        "admin_department_id"
    )

    if not department_id:

        return redirect("home")


    # --------------------------------------------------------
    # GET DEPARTMENT
    # --------------------------------------------------------

    department = get_object_or_404(
        Department,
        id=department_id
    )


    # --------------------------------------------------------
    # GET STUDENTS
    # --------------------------------------------------------

    students = Student.objects.filter(
        department=department
    )


    # --------------------------------------------------------
    # GET YEARS
    # --------------------------------------------------------

    years = (
        students
        .values_list(
            "submission_year",
            flat=True
        )
        .distinct()
        .order_by("-submission_year")
    )


    # --------------------------------------------------------
    # COUNT STUDENTS FOR EACH YEAR
    # --------------------------------------------------------

    year_counts = {}

    for year in years:

        year_counts[year] = students.filter(
            submission_year=year
        ).count()


    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    return render(
        request,
        "admin_dashboard.html",
        {
            "department": department,
            "years": years,
            "year_counts": year_counts,
        }
    )
# ============================================================
# STAFF YEAR STUDENTS
# ============================================================

# ============================================================
# STAFF YEAR STUDENTS
# ============================================================

def admin_year_students(request, year):

    # --------------------------------------------------------
    # CHECK STAFF LOGIN
    # --------------------------------------------------------

    if not request.session.get("admin_logged_in"):
        return redirect("home")

    # --------------------------------------------------------
    # GET STAFF DEPARTMENT
    # --------------------------------------------------------

    department_id = request.session.get(
        "admin_department_id"
    )

    if not department_id:
        return redirect("home")

    # --------------------------------------------------------
    # GET DEPARTMENT
    # --------------------------------------------------------

    department = get_object_or_404(
        Department,
        id=department_id
    )

    # --------------------------------------------------------
    # GET STUDENTS
    # --------------------------------------------------------

    students = Student.objects.filter(
        department=department,
        submission_year=year
    ).order_by("name")

    # --------------------------------------------------------
    # HANDLE ACTION
    # --------------------------------------------------------

    if request.method == "POST":

        student_id = request.POST.get(
            "selected_student"
        )

        action = request.POST.get(
            "action"
        )

        # ----------------------------------------------------
        # CHECK STUDENT SELECTION
        # ----------------------------------------------------

        if not student_id:

            messages.error(
                request,
                "Please select a student first."
            )

            return redirect(
                "admin_year_students",
                year=year
            )

        # ----------------------------------------------------
        # GET STUDENT
        # ----------------------------------------------------

        student = get_object_or_404(
            Student,
            id=student_id,
            department=department,
            submission_year=year
        )

        # ====================================================
        # EDIT
        # ====================================================

        if action == "edit":

            return redirect(
                "admin_edit_student",
                student_id=student.id
            )

        # ====================================================
        # DELETE
        # ====================================================

        elif action == "delete":

            student.delete()

            messages.success(
                request,
                "Student deleted successfully."
            )

            return redirect(
                "admin_year_students",
                year=year
            )

        # ====================================================
        # MAKE REPRESENTATIVE
        # ====================================================

        elif action == "make_representative":

            # Remove representative status from
            # other students in the same department/year

            Student.objects.filter(
                department=department,
                submission_year=year,
                is_leader=True
            ).exclude(
                id=student.id
            ).update(
                is_leader=False
            )

            student.is_leader = True

            student.save(
                update_fields=["is_leader"]
            )

            messages.success(
                request,
                f"{student.name} is now the representative."
            )

            return redirect(
                "admin_year_students",
                year=year
            )

        # ====================================================
        # CANCEL REPRESENTATIVE
        # ====================================================

        elif action == "cancel_representative":

            student.is_leader = False

            student.save(
                update_fields=["is_leader"]
            )

            messages.success(
                request,
                f"{student.name} is no longer the representative."
            )

            return redirect(
                "admin_year_students",
                year=year
            )

    # --------------------------------------------------------
    # DISPLAY PAGE
    # --------------------------------------------------------

    return render(
        request,
        "admin_year_students.html",
        {
            "department": department,
            "students": students,
            "year": year,
        }
    )
# ============================================================
# STAFF EDIT STUDENT
# ============================================================

def admin_edit_student(request, student_id):

    # --------------------------------------------------------
    # CHECK STAFF LOGIN
    # --------------------------------------------------------

    if not request.session.get("admin_logged_in"):

        return redirect("home")


    # --------------------------------------------------------
    # GET STAFF DEPARTMENT
    # --------------------------------------------------------

    department_id = request.session.get(
        "admin_department_id"
    )

    if not department_id:

        return redirect("home")


    # --------------------------------------------------------
    # GET DEPARTMENT
    # --------------------------------------------------------

    department = get_object_or_404(
        Department,
        id=department_id
    )


    # --------------------------------------------------------
    # GET STUDENT
    # IMPORTANT: student must belong to staff department
    # --------------------------------------------------------

    student = get_object_or_404(
        Student,
        id=student_id,
        department=department
    )


    # --------------------------------------------------------
    # EDIT
    # --------------------------------------------------------

    if request.method == "POST":

        form = StaffStudentEditForm(
            request.POST,
            request.FILES,
            instance=student
        )

        if form.is_valid():

            # ------------------------------------------------
            # REPRESENTATIVE HANDLING
            # Only one representative per department/year
            # ------------------------------------------------

            make_leader = form.cleaned_data.get(
                "is_leader"
            )

            if make_leader:

                Student.objects.filter(
                    department=department,
                    submission_year=student.submission_year,
                    is_leader=True
                ).exclude(
                    id=student.id
                ).update(
                    is_leader=False
                )


            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            form.save()

            messages.success(
                request,
                "Student details updated successfully."
            )

            return redirect(
                "admin_year_students",
                year=student.submission_year
            )

    else:

        form = StaffStudentEditForm(
            instance=student
        )


    return render(
        request,
        "student_edit.html",
        {
            "form": form,
            "student": student,
            "department": department,
            "year": student.submission_year,
        }
    )
# ============================================================
# STAFF DELETE STUDENT
# ============================================================

def admin_delete_student(request, student_id):

    if not request.session.get("admin_logged_in"):
        return redirect("home")

    department_id = request.session.get(
        "admin_department_id"
    )

    if not department_id:
        return redirect("home")

    department = get_object_or_404(
        Department,
        id=department_id
    )

    student = get_object_or_404(
        Student,
        id=student_id,
        department=department
    )

    if request.method == "POST":

        student_name = student.name
        year = student.submission_year

        student.delete()

        messages.success(
            request,
            f"Student '{student_name}' deleted successfully."
        )

        return redirect(
            "admin_year_students",
            year=year
        )

    return render(
        request,
        "student_delete_confirm.html",
        {
            "student": student,
            "department": department,
        }
    )
# ============================================================
# STAFF DELETE ENTIRE YEAR
# ============================================================
def year_delete_confirm(request, year):

    if not request.session.get("admin_logged_in"):
        return redirect("home")

    department_id = request.session.get(
        "admin_department_id"
    )

    if not department_id:
        return redirect("home")

    department = get_object_or_404(
        Department,
        id=department_id
    )

    students = Student.objects.filter(
        department=department,
        submission_year=year
    )

    return render(
        request,
        "year_delete_confirm.html",
        {
            "department": department,
            "year": year,
            "student_count": students.count(),
        }
    )
def admin_delete_year(request, year):

    if not request.session.get("admin_logged_in"):
        return redirect("home")

    department_id = request.session.get(
        "admin_department_id"
    )

    if not department_id:
        return redirect("home")

    department = get_object_or_404(
        Department,
        id=department_id
    )

    if request.method == "POST":

        students = Student.objects.filter(
            department=department,
            submission_year=year
        )

        count = students.count()

        students.delete()

        messages.success(
            request,
            f"{count} student record(s) from {year} deleted successfully."
        )

        return redirect(
            "admin_dashboard"
        )

    return redirect(
        "year_delete_confirm",
        year=year
    )
def admin_make_representative(request, student_id):

    # --------------------------------------------------------
    # CHECK STAFF LOGIN
    # --------------------------------------------------------

    if not request.session.get("admin_logged_in"):

        return redirect("home")


    # --------------------------------------------------------
    # GET STAFF DEPARTMENT
    # --------------------------------------------------------

    department_id = request.session.get(
        "admin_department_id"
    )

    if not department_id:

        return redirect("home")


    # --------------------------------------------------------
    # GET DEPARTMENT
    # --------------------------------------------------------

    department = get_object_or_404(
        Department,
        id=department_id
    )


    # --------------------------------------------------------
    # ONLY POST IS ALLOWED
    # --------------------------------------------------------

    if request.method != "POST":

        return redirect(
            "admin_dashboard"
        )


    # --------------------------------------------------------
    # GET STUDENT
    # Student MUST belong to this department
    # --------------------------------------------------------

    student = get_object_or_404(
        Student,
        id=student_id,
        department=department
    )


    # --------------------------------------------------------
    # REMOVE REPRESENTATIVE STATUS FROM
    # OTHER STUDENTS OF SAME DEPARTMENT + YEAR
    # --------------------------------------------------------

    Student.objects.filter(
        department=department,
        submission_year=student.submission_year,
        is_leader=True
    ).exclude(
        id=student.id
    ).update(
        is_leader=False
    )


    # --------------------------------------------------------
    # MAKE SELECTED STUDENT REPRESENTATIVE
    # --------------------------------------------------------

    student.is_leader = True

    student.save(
        update_fields=["is_leader"]
    )


    # --------------------------------------------------------
    # SUCCESS MESSAGE
    # --------------------------------------------------------

    messages.success(
        request,
        f"{student.name} is now the representative for {student.submission_year}."
    )


    # --------------------------------------------------------
    # RETURN TO SAME YEAR
    # --------------------------------------------------------

    return redirect(
        "admin_year_students",
        year=student.submission_year
    )
# ============================================================
# STUDENT PROVISIONAL ID DOWNLOAD PAGE
# ============================================================

def student_download(request):

    # --------------------------------------------------------
    # CHECK STUDENT LOGIN
    # --------------------------------------------------------

    student_id = request.session.get(
        "student_id"
    )

    if not student_id:

        return redirect(
            "home"
        )


    # --------------------------------------------------------
    # GET LOGGED-IN STUDENT
    # --------------------------------------------------------

    student = get_object_or_404(
        Student,
        id=student_id
    )


    # --------------------------------------------------------
    # CHECK REPRESENTATIVE
    # --------------------------------------------------------

    if not student.is_leader:

        return redirect(
            "student_status"
        )


    # --------------------------------------------------------
    # GET DEPARTMENT
    # --------------------------------------------------------

    department = student.department


    # --------------------------------------------------------
    # GET STUDENTS FOR SAME
    # DEPARTMENT + YEAR
    # --------------------------------------------------------

    students = Student.objects.filter(
        department=department,
        submission_year=student.submission_year
    )


    # --------------------------------------------------------
    # COUNT STUDENTS
    # --------------------------------------------------------

    student_count = students.count()


    # --------------------------------------------------------
    # DOWNLOAD PAGE
    # --------------------------------------------------------

    return render(
        request,
        "student_download.html",
        {
            "student": student,
            "department": department,
            "year": student.submission_year,
            "students": students,
            "student_count": student_count,
        }
    )
    return response
# ============================================================
# STUDENT DOWNLOAD ALL PROVISIONAL IDS
# 3 ID CARDS PER A4 PAGE
# ============================================================

# ============================================================
# STUDENT DOWNLOAD ALL NEW PROVISIONAL IDS
# 3 ID CARDS PER A4 PAGE
# ============================================================

def download_provisional_id(request):

    # ========================================================
    # CHECK STUDENT LOGIN
    # ========================================================

    student_id = request.session.get(
        "student_id"
    )

    if not student_id:

        return redirect(
            "home"
        )

    # ========================================================
    # GET LOGGED-IN STUDENT
    # ========================================================

    student = get_object_or_404(
        Student,
        id=student_id
    )

    # ========================================================
    # CHECK REPRESENTATIVE
    # ========================================================

    if not student.is_leader:

        messages.error(
            request,
            "You are not authorized to download the Provisional ID."
        )

        return redirect(
            "student_status"
        )

    # ========================================================
    # GET DEPARTMENT
    # ========================================================

    department = student.department

    # ========================================================
    # YEAR
    # ========================================================

    year = student.submission_year

    # ========================================================
    # GET ONLY NOT-YET-GENERATED STUDENTS
    # ========================================================

    students = list(
        Student.objects.filter(
            department=department,
            submission_year=year,
            pdf_generated=False
        ).order_by(
            "name"
        )
    )

    # ========================================================
    # NOTHING NEW TO GENERATE
    # ========================================================

    if not students:

        messages.info(
            request,
            f"All provisional ID cards for {year} have already been generated."
        )

        return redirect(
            "student_download"
        )

    # ========================================================
    # PREPARE PDF DATA
    # ========================================================

    pdf_students = []

    for item in students:

        photo_path = None

        if item.photo:

            try:

                photo_path = item.photo.path

            except Exception:

                photo_path = None

        pdf_students.append(
            {
                "name": item.name.upper(),

                "roll_no": (
                    item.roll_no.upper()
                    or ""
                ),

                # IMPORTANT:
                # CLASS COMES FROM DEPARTMENT
                "class_name": (
                    department.class_name
                ),

                "to_place": item.to_place.upper(),

                "photo": photo_path,
            }
        )

    # ========================================================
    # CREATE PDF IN MEMORY
    # ========================================================

    output = BytesIO()

    c = canvas.Canvas(
        output,
        pagesize=A4
    )

    PAGE_WIDTH, PAGE_HEIGHT = A4

    # ========================================================
    # CARD SETTINGS
    # ========================================================

    card_x = 60

    card_width = 475

    card_height = 205

    top_margin = 55

    bottom_margin = 55

    gap = (
        PAGE_HEIGHT
        - top_margin
        - bottom_margin
        - (card_height * 3)
    ) / 2

    # ========================================================
    # CARD POSITIONS
    # ========================================================

    card_positions = [

        PAGE_HEIGHT
        - top_margin
        - card_height,

        PAGE_HEIGHT
        - top_margin
        - card_height
        - card_height
        - gap,

        bottom_margin,
    ]

    # ========================================================
    # CUTTING LINE
    # ========================================================

    def draw_cutting_line(y):

        c.saveState()

        c.setStrokeColorRGB(
            0.75,
            0.75,
            0.75
        )

        c.setLineWidth(
            0.35
        )

        c.setDash(
            2,
            3
        )

        c.line(
            42,
            y,
            PAGE_WIDTH - 42,
            y
        )

        c.restoreState()

    # ========================================================
    # FIT TEXT
    # ========================================================

    def draw_fitted_text(
        text,
        x,
        y,
        max_width,
        font="Times-Bold",
        font_size=8
    ):

        text = str(
            text
        )

        size = font_size

        while size > 5:

            text_width = stringWidth(
                text,
                font,
                size
            )

            if text_width <= max_width:

                break

            size -= 0.25

        c.setFont(
            font,
            size
        )

        c.drawString(
            x,
            y,
            text
        )

    # ========================================================
    # DRAW PHOTO
    # ========================================================

    def draw_photo(
        photo_path,
        x,
        y,
        width,
        height
    ):

        c.setStrokeColorRGB(
            0,
            0,
            0
        )

        c.setLineWidth(
            0.8
        )

        c.rect(
            x,
            y,
            width,
            height,
            fill=0,
            stroke=1
        )

        if not photo_path:

            return

        if not os.path.isfile(
            photo_path
        ):

            return

        try:

            image = PILImage.open(
                photo_path
            )

            image_width, image_height = (
                image.size
            )

            scale = min(
                width / image_width,
                height / image_height
            )

            final_width = (
                image_width * scale
            )

            final_height = (
                image_height * scale
            )

            final_x = (
                x
                + (
                    width
                    - final_width
                ) / 2
            )

            final_y = (
                y
                + (
                    height
                    - final_height
                ) / 2
            )

            c.drawImage(
                ImageReader(
                    photo_path
                ),
                final_x,
                final_y,
                width=final_width,
                height=final_height,
                preserveAspectRatio=True,
                mask="auto"
            )

            c.setStrokeColorRGB(
                0,
                0,
                0
            )

            c.rect(
                x,
                y,
                width,
                height,
                fill=0,
                stroke=1
            )

        except Exception:

            pass

    # ========================================================
    # DRAW ONE ID CARD
    # ========================================================

    def draw_id_card(
        data,
        card_y
    ):

        card_top = (
            card_y
            + card_height
        )

        # ----------------------------------------------------
        # BORDER
        # ----------------------------------------------------

        c.setStrokeColorRGB(
            0,
            0,
            0
        )

        c.setLineWidth(
            0.9
        )

        c.rect(
            card_x,
            card_y,
            card_width,
            card_height,
            fill=0,
            stroke=1
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        c.setFillColorRGB(
            0,
            0,
            0
        )

        c.setFont(
            "Times-Bold",
            8.5
        )

        c.drawCentredString(
            PAGE_WIDTH / 2,
            card_top - 14,
            "GOVERNMENT ARTS COLLEGE (AUTONOMOUS)"
        )

        c.drawCentredString(
            PAGE_WIDTH / 2,
            card_top - 25,
            "COIMBATORE - 641 018"
        )

        c.drawCentredString(
            PAGE_WIDTH / 2,
            card_top - 36,
            "PROVISIONAL IDENTITY CARD"
        )

        # ----------------------------------------------------
        # POSITIONS
        # ----------------------------------------------------

        label_x = (
            card_x + 20
        )

        colon_x = (
            card_x + 155
        )

        value_x = (
            card_x + 168
        )

        name_y = (
            card_top - 58
        )

        roll_y = (
            card_top - 78
        )

        class_y = (
            card_top - 98
        )

        tutor_y = (
            card_top - 119
        )

        hod_y = (
            card_top - 148
        )

        # ----------------------------------------------------
        # FONT
        # ----------------------------------------------------

        c.setFont(
            "Times-Bold",
            7.5
        )

        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        c.drawString(
            label_x,
            name_y,
            "NAME"
        )

        c.drawString(
            colon_x,
            name_y,
            ":"
        )

        draw_fitted_text(
            data["name"],
            value_x,
            name_y,
            205
        )

        # ----------------------------------------------------
        # ROLL NO
        # ----------------------------------------------------

        c.drawString(
            label_x,
            roll_y,
            "ROLL NO"
        )

        c.drawString(
            colon_x,
            roll_y,
            ":"
        )

        draw_fitted_text(
            data["roll_no"],
            value_x,
            roll_y,
            205
        )

        # ----------------------------------------------------
        # CLASS
        # ----------------------------------------------------

        c.drawString(
            label_x,
            class_y,
            "CLASS"
        )

        c.drawString(
            colon_x,
            class_y,
            ":"
        )

        draw_fitted_text(
            data["class_name"],
            value_x,
            class_y,
            190
        )

        # ----------------------------------------------------
        # PHOTO
        # ----------------------------------------------------

        photo_width = 48

        photo_height = 60

        photo_x = (
            card_x
            + card_width
            - photo_width
            - 30
        )

        photo_y = (
            card_top
            - 112
        )

        draw_photo(
            data["photo"],
            photo_x,
            photo_y,
            photo_width,
            photo_height
        )

        # ----------------------------------------------------
        # CLASS TUTOR
        # ----------------------------------------------------

        c.drawString(
            label_x,
            tutor_y,
            "CLASS TUTOR'S SIGN."
        )

        c.drawString(
            colon_x,
            tutor_y,
            ":"
        )

        # ----------------------------------------------------
        # HOD
        # ----------------------------------------------------

        c.drawString(
            label_x,
            hod_y,
            "HOD'S SIGNATURE"
        )

        c.drawString(
            colon_x,
            hod_y,
            ":"
        )

        # ----------------------------------------------------
        # BOTTOM SECTION
        # ----------------------------------------------------

        bottom_height = 25

        bottom_y = card_y

        c.line(
            card_x,
            bottom_y + bottom_height,
            card_x + card_width,
            bottom_y + bottom_height
        )

        from_width = 55

        college_width = 215

        to_width = 45

        x1 = (
            card_x
            + from_width
        )

        x2 = (
            x1
            + college_width
        )

        x3 = (
            x2
            + to_width
        )

        # ----------------------------------------------------
        # VERTICAL LINES
        # ----------------------------------------------------

        c.line(
            x1,
            bottom_y,
            x1,
            bottom_y + bottom_height
        )

        c.line(
            x2,
            bottom_y,
            x2,
            bottom_y + bottom_height
        )

        c.line(
            x3,
            bottom_y,
            x3,
            bottom_y + bottom_height
        )

        # ----------------------------------------------------
        # FROM
        # ----------------------------------------------------

        c.setFont(
            "Times-Bold",
            7
        )

        c.drawString(
            card_x + 5,
            bottom_y + 8,
            "FROM :"
        )

        # ----------------------------------------------------
        # COLLEGE
        # ----------------------------------------------------

        draw_fitted_text(
            "GOVT ARTS COLLEGE COIMBATORE",
            x1 + 5,
            bottom_y + 8,
            college_width - 10,
            "Times-Bold",
            7
        )

        # ----------------------------------------------------
        # TO
        # ----------------------------------------------------

        c.drawString(
            x2 + 7,
            bottom_y + 8,
            "TO:"
        )

        # ----------------------------------------------------
        # DESTINATION
        # ----------------------------------------------------

        draw_fitted_text(
            data["to_place"],
            x3 + 5,
            bottom_y + 8,
            card_x + card_width - x3 - 10,
            "Times-Bold",
            7
        )

    # ========================================================
    # GENERATE PAGES
    # ========================================================

    for page_start in range(
        0,
        len(pdf_students),
        3
    ):

        page_students = pdf_students[
            page_start:
            page_start + 3
        ]

        # ----------------------------------------------------
        # TOP CUTTING LINE
        # ----------------------------------------------------

        draw_cutting_line(
            PAGE_HEIGHT - 28
        )

        # ----------------------------------------------------
        # CARDS
        # ----------------------------------------------------

        for index, data in enumerate(
            page_students
        ):

            draw_id_card(
                data,
                card_positions[index]
            )

            # ------------------------------------------------
            # CUTTING LINE AFTER CARD
            # ------------------------------------------------

            if index < (
                len(page_students) - 1
            ):

                cut_y = (
                    card_positions[index]
                    - gap / 2
                )

                draw_cutting_line(
                    cut_y
                )

        # ----------------------------------------------------
        # BOTTOM CUTTING LINE
        # ----------------------------------------------------

        draw_cutting_line(
            28
        )

        c.showPage()

    # ========================================================
    # FINISH PDF
    # ========================================================

    c.save()

    output.seek(
        0
    )

    # ========================================================
    # MARK STUDENTS AS GENERATED
    #
    # ONLY AFTER PDF SUCCESSFULLY CREATED
    # ========================================================

    generated_ids = [
        item.id
        for item in students
    ]

    Student.objects.filter(
        id__in=generated_ids,
        pdf_generated=False
    ).update(
        pdf_generated=True
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    response = HttpResponse(
        output.getvalue(),
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; '
        f'filename="provisional_ids_{year}.pdf"'
    )

    return response
# ============================================================
# STAFF CANCEL REPRESENTATIVE
# ============================================================

# ============================================================
# STAFF CANCEL STUDENT REPRESENTATIVE
# ============================================================

def admin_cancel_representative(request, student_id):

    # --------------------------------------------------------
    # CHECK STAFF LOGIN
    # --------------------------------------------------------

    if not request.session.get("admin_logged_in"):
        return redirect("home")

    # --------------------------------------------------------
    # GET STAFF DEPARTMENT
    # --------------------------------------------------------

    department_id = request.session.get(
        "admin_department_id"
    )

    if not department_id:
        return redirect("home")

    # --------------------------------------------------------
    # GET DEPARTMENT
    # --------------------------------------------------------

    department = get_object_or_404(
        Department,
        id=department_id
    )

    # --------------------------------------------------------
    # ONLY POST IS ALLOWED
    # --------------------------------------------------------

    if request.method != "POST":
        return redirect("admin_dashboard")

    # --------------------------------------------------------
    # GET STUDENT
    # Student must belong to staff department
    # --------------------------------------------------------

    student = get_object_or_404(
        Student,
        id=student_id,
        department=department
    )

    # --------------------------------------------------------
    # CANCEL REPRESENTATIVE
    # --------------------------------------------------------

    student.is_leader = False

    student.save(
        update_fields=["is_leader"]
    )

    # --------------------------------------------------------
    # SUCCESS MESSAGE
    # --------------------------------------------------------

    messages.success(
        request,
        f"{student.name} is no longer the representative."
    )

    # --------------------------------------------------------
    # RETURN TO SAME YEAR
    # --------------------------------------------------------

    return redirect(
        "admin_year_students",
        year=student.submission_year
    )