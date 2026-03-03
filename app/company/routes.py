from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import Company, PlacementDrive, Application, Student
from . import company_bp


# Role protection decorator
def company_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != "company":
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


# ---------------- Dashboard ----------------
@company_bp.route("/")
@login_required
@company_required
def dashboard():
    return render_template("company/dashboard.html")


# ---------------- Post Job ----------------
@company_bp.route("/post-job", methods=["GET", "POST"])
@login_required
@company_required
def post_job():
    company = Company.query.filter_by(user_id=current_user.id).first()
    if not company:
        flash("Please complete company registration first.")
        return redirect(url_for("company.dashboard"))
    
    if request.method == "POST":
        job_title = request.form.get("job_title")
        description = request.form.get("description")
        eligibility = request.form.get("eligibility")
        deadline = request.form.get("deadline")

        new_drive = PlacementDrive(
            job_title=job_title,
            description=description,
            eligibility=eligibility,
            deadline=deadline,
            company_id=company.id,
            status="pending"
        )

        db.session.add(new_drive)
        db.session.commit()

        flash("Placement drive created successfully!")
        return redirect(url_for("company.dashboard"))

    return render_template("company/post_job.html")


# ---------------- View Jobs ----------------
@company_bp.route("/jobs")
@login_required
@company_required
def view_jobs():
    company = Company.query.filter_by(user_id=current_user.id).first()
    if not company:
        flash("Company profile not found.")
        return redirect(url_for("company.dashboard"))
    
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    return render_template("company/jobs.html", drives=drives)


# ---------------- View Applicants ----------------
@company_bp.route("/applicants/<int:drive_id>")
@login_required
@company_required
def view_applicants(drive_id):
    # Verify company owns this drive
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        flash("Placement drive not found.")
        return redirect(url_for("company.view_jobs"))
    
    company = Company.query.filter_by(user_id=current_user.id).first()
    if not company or drive.company_id != company.id:
        flash("Unauthorized access.")
        return redirect(url_for("company.view_jobs"))
    
    applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template("company/applicants.html", applications=applications, drive=drive)