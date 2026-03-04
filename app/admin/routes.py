from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import User, Company, PlacementDrive, Application
from . import admin_bp


# ================= ADMIN DASHBOARD =================
@admin_bp.route("/dashboard")
@login_required
def dashboard():

    if current_user.role != "admin":
        flash("Access denied!", "error")
        return redirect(url_for("auth.login"))

    # Counts
    total_student = User.query.filter_by(role="student").count()
    total_companies = User.query.filter_by(role="company").count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()

    view = request.args.get("view")

    # Pending companies
    all_pending_companies = Company.query.filter_by(
        approval_status="pending",
        is_blacklisted=False
    ).all()

    # Blacklisted companies
    all_blocked_companies = Company.query.filter_by(
        is_blacklisted=True
    ).all()

    # Pending drives
    pending_drives = PlacementDrive.query.filter_by(
        status="pending"
    ).all()

    return render_template(
        "admin/dashboard.html",
        total_student=total_student,
        total_companies=total_companies,
        total_drives=total_drives,
        total_applications=total_applications,
        view=view,
        all_pending_companies=all_pending_companies,
        all_blocked_companies=all_blocked_companies,
        pending_drives=pending_drives
    )


# ================= VIEW TOGGLE =================
@admin_bp.route("/a_admin")
@login_required
def a_admin():

    view = request.args.get("view")

    return redirect(url_for("admin.dashboard", view=view))


# ================= APPROVE COMPANY =================
@admin_bp.route("/approve_company/<int:id>")
@login_required
def approve_company(id):

    company = Company.query.get_or_404(id)

    company.approval_status = "approved"
    company.is_blacklisted = False

    db.session.commit()

    flash("Company approved successfully", "success")

    return redirect(url_for("admin.dashboard"))


# ================= REJECT / BLACKLIST COMPANY =================
@admin_bp.route("/block_company/<int:id>")
@login_required
def block_company(id):

    company = Company.query.get_or_404(id)

    company.is_blacklisted = True

    db.session.commit()

    flash("Company moved to blacklist", "warning")

    return redirect(url_for("admin.dashboard", view="blacklist"))


# ================= WHITELIST COMPANY =================
@admin_bp.route("/pending/<int:id>")
@login_required
def pending_company(id):

    company = Company.query.get_or_404(id)

    company.is_blacklisted = False
    company.approval_status = "approved"

    db.session.commit()

    flash("Company removed from blacklist", "success")

    return redirect(url_for("admin.dashboard"))


# ================= APPROVE DRIVE =================
@admin_bp.route("/approve_drives/<int:id>")
@login_required
def approve_drives(id):

    drive = PlacementDrive.query.get_or_404(id)

    drive.status = "approved"

    db.session.commit()

    flash("Drive approved successfully", "success")

    return redirect(url_for("admin.dashboard"))


# ================= REJECT DRIVE =================
@admin_bp.route("/drives_reject/<int:id>")
@login_required
def drives_reject(id):

    drive = PlacementDrive.query.get_or_404(id)

    drive.status = "rejected"

    db.session.commit()

    flash("Drive rejected", "danger")

    return redirect(url_for("admin.dashboard"))