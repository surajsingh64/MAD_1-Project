from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db, student
from app.models import User, Company, PlacementDrive, Application
from . import admin_bp
from app.models import Student


#  here we are checking if the user is admin or not
def admin_required():
    if current_user.role != "admin":
        flash("Access denied!", "danger")
        return False
    return True


# dashboard route
@admin_bp.route("/dashboard")
@login_required
def dashboard():

    if not admin_required():
        return redirect(url_for("auth.login"))

    total_student = User.query.filter_by(role="student").count()
    total_companies = Company.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()

    view = request.args.get("view")

    pending_companies = Company.query.filter_by(
        approval_status="pending",
        is_blacklisted=False
    ).all()

    blacklisted_companies = Company.query.filter_by(
        is_blacklisted=True
    ).all()

    pending_drives = PlacementDrive.query.filter_by(
        status="pending"
    ).all()
 #placement drives
    drive_view = request.args.get("drive_view")
 # pending drives
    pending_drives = PlacementDrive.query.filter_by(status='pending').all()
    reject_drives = PlacementDrive.query.filter_by(status='rejected').all()

    return render_template(
        "admin/dashboard.html",
        total_student=total_student,
        total_companies=total_companies,
        total_drives=total_drives,
        total_applications=total_applications,
        view=view,
        pending_companies=pending_companies,
        blacklisted_companies=blacklisted_companies,
        pending_drives=pending_drives,
        reject_drives=reject_drives,
        drive_view=drive_view
    )

# view students
@admin_bp.route("/students")
@login_required
def students():

    if current_user.role != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("auth.login"))

    students = User.query.filter_by(role="student").all()

    return render_template(
        "admin/students.html",
        students=students
    )

# view toggle for companies and drives
@admin_bp.route("/view")
@login_required
def view_toggle():

    view = request.args.get("view")

    return redirect(url_for("admin.dashboard", view=view))


# aprove company
@admin_bp.route("/approve_company/<int:id>")
@login_required
def approve_company(id):

    if not admin_required():
        return redirect(url_for("auth.login"))

    company = Company.query.get_or_404(id)

    company.approval_status = "approved"
    company.is_blacklisted = False

    db.session.commit()
    flash("Company approved successfully", "success")

    return redirect(url_for("admin.dashboard"))

# reject company
@admin_bp.route("/reject_company/<int:id>")
@login_required
def reject_company(id):
    if not admin_required():
        return redirect(url_for("auth.login"))
    company = Company.query.get_or_404(id)
    company.approval_status = "rejected"
    db.session.commit()
    flash("Company rejected", "danger")
    return redirect(url_for("admin.dashboard"))


# blacklisted company
@admin_bp.route("/block_company/<int:id>")
@login_required
def block_company(id):

    if not admin_required():
        return redirect(url_for("auth.login"))

    company = Company.query.get_or_404(id)

    company.is_blacklisted = True

    db.session.commit()

    flash("Company moved to blacklist", "warning")

    return redirect(url_for("admin.dashboard", view="blacklist"))


# remove from blacklist
@admin_bp.route("/whitelist_company/<int:id>")
@login_required
def whitelist_company(id):

    if not admin_required():
        return redirect(url_for("auth.login"))

    company = Company.query.get_or_404(id)

    company.is_blacklisted = False
    company.approval_status = "approved"

    db.session.commit()

    flash("Company removed from blacklist", "success")

    return redirect(url_for("admin.dashboard"))

# pending company
@admin_bp.route("/pending_company/<int:id>")
@login_required
def pending_company(id):

    if not admin_required():
        return redirect(url_for("auth.login"))
    company = Company.query.get_or_404(id)
    company.approval_status = "pending"
    company.is_blacklisted = False
    db.session.commit()
    flash("Company moved to pending list", "info")
    return redirect(url_for("admin.dashboard"))

# ------------------------drive-----------------------------


# approve drive
@admin_bp.route("/approve_drive/<int:id>")
@login_required
def approve_drive(id):

    if not admin_required():
        return redirect(url_for("auth.login"))

    drive = PlacementDrive.query.get_or_404(id)

    drive.status = "approved"

    db.session.commit()

    flash("Drive approved successfully", "success")

    return redirect(url_for("admin.dashboard"))


#reject drive
@admin_bp.route("/reject_drive/<int:id>")
@login_required
def reject_drive(id):

    if not admin_required():
        return redirect(url_for("auth.login"))

    drive = PlacementDrive.query.get_or_404(id)
    drive.status = "rejected"
    db.session.commit()
    flash("Drive rejected", "danger")
    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/companies")
@login_required
def companies():

    companies = Company.query.all()

    return render_template(
        "admin/companies.html",
        companies=companies
    )

@admin_bp.route("/drives")
@login_required
def drives():

    drives = PlacementDrive.query.all()

    return render_template(
        "admin/drives.html",
        drives=drives
    )

# blacklist student
@admin_bp.route("/toggle_blacklist/<int:id>")
@login_required
def toggle_blacklist(id):

    student = Student.query.filter_by(user_id=id).first()

    if student:
        student.is_blacklisted = not student.is_blacklisted
        db.session.commit()

    flash("Student status updated", "success")

    return redirect(url_for("admin.students"))