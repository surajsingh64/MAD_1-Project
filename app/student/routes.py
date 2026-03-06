from flask import render_template, redirect, request, url_for
from flask_login import login_required, current_user
from app.models import Student, PlacementDrive, Application
from app import db
from . import student_bp


@student_bp.route("/dashboard")
@login_required
def dashboard():

    if current_user.role != "student":
        return "Unauthorized", 403

    student = Student.query.filter_by(user_id=current_user.id).first()

    if not student:
        return "Student profile not found", 404

    available_drives = PlacementDrive.query.filter_by(status="open").all()

    applications = Application.query.filter_by(student_id=student.id).all()

    total_applied = len(applications)

    total_shortlisted = Application.query.filter_by(
        student_id=student.id,
        status="shortlisted"
    ).count()

    total_rejected = Application.query.filter_by(
        student_id=student.id,
        status="rejected"
    ).count()

    return render_template(
        "student/dashboard.html",
        student=student,
        available_drives=available_drives,
        applications=applications,
        total_applied=total_applied,
        total_shortlisted=total_shortlisted,
        total_rejected=total_rejected
    )


@student_bp.route("/apply_drive/<int:drive_id>", methods=["POST"])
@login_required
def apply_drive(drive_id):

    if current_user.role != "student":
        return "Unauthorized", 403

    student = Student.query.filter_by(user_id=current_user.id).first()

    if not student:
        return "Student profile not found", 404

    if student.is_blacklisted:
        return "You are blacklisted and cannot apply", 403

    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.status != "open":
        return "Drive not available", 404

    existing_application = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive_id
    ).first()

    if existing_application:
        return "Already applied", 400

    new_application = Application(
        student_id=student.id,
        drive_id=drive_id,
        status="applied"
    )

    db.session.add(new_application)
    db.session.commit()

    return redirect(url_for("student.dashboard"))

@student_bp.route("/profile/<int:student_id>", methods=["GET", "POST"])
@login_required
def student_profile(student_id):

    if current_user.role != "student":
        return "Unauthorized", 403

    student = Student.query.filter_by(user_id=current_user.id).first()

    if not student or student.id != student_id:
        return "Student profile not found", 404

    if request.method == "POST":

        student.name = request.form.get("name")
        student.branch = request.form.get("branch")
        student.phone = request.form.get("phone")
        student.cgpa = request.form.get("cgpa")

        db.session.commit()

        return redirect(url_for("student.student_profile", student_id=student_id))

    return render_template("student/profile.html", student=student)

@student_bp.route("/history/<int:student_id>")
@login_required
def student_history(student_id):

    if current_user.role != "student":
        return "Unauthorized", 403

    student = Student.query.filter_by(user_id=current_user.id).first()

    if not student or student.id != student_id:
        return "Student profile not found", 404

    applications = Application.query.filter_by(student_id=student.id).all()

    return render_template(
        "student/history.html",
        applications=applications
    )

@student_bp.route("/available_drives")
@login_required
def available_drives():

    student = Student.query.filter_by(user_id=current_user.id).first()

    drives = PlacementDrive.query.filter_by(status="open").all()

    return render_template(
        "student/available_drive.html",
        drives=drives,
        student=student
    )

@student_bp.route("/applied_drives")
@login_required
def applied_drives():

    student = Student.query.filter_by(user_id=current_user.id).first()

    applications = Application.query.filter_by(student_id=student.id).all()

    return render_template(
        "student/applied_drive.html",
        applications=applications
    )


@student_bp.route("/stats")
@login_required
def stats():

    student = Student.query.filter_by(user_id=current_user.id).first()

    total_applied = Application.query.filter_by(student_id=student.id).count()
    shortlisted = Application.query.filter_by(student_id=student.id, status="shortlisted").count()
    rejected = Application.query.filter_by(student_id=student.id, status="rejected").count()

    return render_template(
        "student/stats.html",
        total_applied=total_applied,
        shortlisted=shortlisted,
        rejected=rejected
    )