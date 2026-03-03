from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import PlacementDrive, Student, Application
from . import student_bp


# ---------------- Role Decorator ----------------
def student_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != "student":
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


# ---------------- Dashboard ----------------
@student_bp.route("/")
@login_required
@student_required
def dashboard():
    return render_template("student/dashboard.html")


# ---------------- View All Jobs ----------------
@student_bp.route("/jobs")
@login_required
@student_required
def view_jobs():
    drives = PlacementDrive.query.filter_by(status='approved').all()
    return render_template("student/jobs.html", drives=drives)


# ---------------- Apply to Job ----------------
@student_bp.route("/apply/<int:drive_id>")
@login_required
@student_required
def apply_job(drive_id):
    # Get student profile
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if not student:
        flash("Please complete your profile first.")
        return redirect(url_for("student.profile"))

    # Check if already applied
    existing_application = Application.query.filter_by(
        drive_id=drive_id,
        student_id=student.id
    ).first()

    if existing_application:
        flash("You already applied for this placement drive.")
        return redirect(url_for("student.view_jobs"))

    new_application = Application(
        drive_id=drive_id,
        student_id=student.id,
        status="applied"
    )

    db.session.add(new_application)
    db.session.commit()

    flash("Application submitted successfully!")
    return redirect(url_for("student.view_jobs"))


# ---------------- My Applications ----------------
@student_bp.route("/applications")
@login_required
@student_required
def my_applications():
    applications = Application.query.filter_by(
        student_id=current_user.id
    ).all()

    return render_template("student/applications.html", applications=applications)


# ---------------- Profile ----------------
@student_bp.route("/profile")
@login_required
@student_required
def profile():
    return render_template("student/profile.html")