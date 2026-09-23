from django.urls import path
from . import views


urlpatterns = [
    path(
    "",
    views.welcome,
    name="welcome"
),

path(
    "home/",
    views.home,
    name="home"
),

    # =========================================
    # DEPARTMENT OPTIONS
    # =========================================

    path(
        "department/<int:department_id>/",
        views.department_options,
        name="department_options"
    ),

    # =========================================
    # STUDENT LOGIN
    # =========================================

    path(
        "department/<int:department_id>/login/",
        views.student_login,
        name="student_login"
    ),

    # =========================================
    # ADMIN LOGIN
    # =========================================

    path(
        "department/<int:department_id>/admin-login/",
        views.admin_login,
        name="admin_login"
    ),

    # =========================================
    # ADMIN DASHBOARD
    # =========================================

    path(
        "staff/dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),

    # =========================================
    # STUDENT FORM
    # =========================================

    path(
        "student/form/",
        views.student_form,
        name="student_form"
    ),

    # =========================================
    # STUDENT PREVIEW
    # =========================================

    path(
        "student/preview/",
        views.student_preview,
        name="student_preview"
    ),

    # =========================================
    # STUDENT CONFIRM
    # =========================================

    path(
        "student/confirm/",
        views.student_confirm,
        name="student_confirm"
    ),

    # =========================================
    # STUDENT STATUS
    # =========================================

    path(
        "student/status/",
        views.student_status,
        name="student_status"
    ),
    path(
    "staff/year/<int:year>/",
    views.admin_year_students,
    name="admin_year_students"
),
path(
    "staff/",
    views.admin_department_select,
    name="admin_department_select"
),
# =========================================
# EDIT STUDENT
# =========================================

path(
    "staff/student/<int:student_id>/edit/",
    views.admin_edit_student,
    name="admin_edit_student"
),

# =========================================
# DELETE STUDENT
# =========================================

path(
    "staff/student/<int:student_id>/delete/",
    views.admin_delete_student,
    name="admin_delete_student"
),

# =========================================
# DELETE ENTIRE YEAR
# =========================================
# =========================================
# DELETE ENTIRE YEAR - CONFIRMATION
# =========================================


path(
    "staff/year/<int:year>/delete/",
    views.year_delete_confirm,
    name="year_delete_confirm"
),

path(
    "staff/year/<int:year>/delete/confirm/",
    views.admin_delete_year,
    name="admin_delete_year"
),
path(
    "staff/student/<int:student_id>/make-representative/",
    views.admin_make_representative,
    name="admin_make_representative"
),
path(
    "student/download/",
    views.student_download,
    name="student_download"
),

path(
    "student/download/pdf/",
    views.download_provisional_id,
    name="download_provisional_id"
),
path(
    "staff/student/<int:student_id>/cancel-representative/",
    views.admin_cancel_representative,
    name="admin_cancel_representative"
),
]