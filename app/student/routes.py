from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import login_required, current_user
from . import student_bp as student
from app.models import Student, PlacementDrive, Application, Company
from app import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime,date
"""
dashboard()
apply_drive()
stu_profile()
organisation()
application()
explore()
history()"""

def student_required():
    if current_user.role != "student":
        abort(403)
    if not current_user.student:
        abort(404)
    return current_user.student


# Dashboard 
@student.route('/student/dashboard')
@login_required
def dashboard():

    stu = student_required()
    total_applied = Application.query.filter_by(student_id=stu.id).count()
    total_shortlisted = Application.query.filter_by(student_id=stu.id, status="shortlisted").count()
    total_selected = Application.query.filter_by(student_id=stu.id, status="selected").count()
    total_rejected = Application.query.filter_by(student_id=stu.id, status="rejected").count()
    applications = Application.query.filter_by(student_id=stu.id).all()
    applied_ids = [app.drive_id for app in applications]
    #available drive
    # In dashboard()

    today = date.today()

    available_drives = PlacementDrive.query.filter(
            PlacementDrive.status == "open",
            PlacementDrive.deadline >= today
        ).all()

    companies = []
    seen = set()
    for d in available_drives:
            if d.company_id not in seen:
                companies.append(d.company)
                seen.add(d.company_id)

    open_drive_count = len(available_drives)

    return render_template(
            'student/s_dashboard.html',
            student=stu,
            applications=applications,
            total_applied=total_applied,
            total_shortlisted=total_shortlisted,
            total_selected=total_selected,
            total_rejected=total_rejected,
            drives=available_drives,
            applied_drive_ids=applied_ids,
            available_drives=available_drives,
            open_drive_count=open_drive_count,
            companies=companies   
        )


# 
@student.route('/student/apply/<int:drive_id>', methods=["POST"])
@login_required
def apply_drive(drive_id):

    stu = student_required()

    if stu.is_blacklisted:
        flash("You are blacklisted!", "danger")
        return redirect(url_for("student.dashboard"))

    drive = PlacementDrive.query.get_or_404(drive_id)  

    if drive.status != "open":
        flash("Drive is not open", "warning")
        return redirect(url_for("student.dashboard"))

    if drive.deadline and drive.deadline < datetime.now().date():
        flash("Deadline passed", "warning")
        return redirect(url_for("student.dashboard"))

    existing = Application.query.filter_by(
        student_id=stu.id,
        drive_id=drive_id
    ).first()

    if existing:
        flash("Already applied!", "info")
        return redirect(url_for("student.dashboard"))

    new_app = Application(
        student_id=stu.id,
        drive_id=drive_id,
        status="applied"
    )

    db.session.add(new_app)
    db.session.commit()

    flash("Applied successfully!", "success")
    return redirect(url_for("student.dashboard")) 


# profile
allowed_extension = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extension


@student.route('/student/stu_profile/<int:id>', methods=['POST','GET'])
@login_required
def stu_profile(id):

    stu = student_required()

    if stu.id != id:
        abort(403)

    if request.method == "POST":

        stu.name = request.form.get("name")
        stu.roll_no = request.form.get("roll_no")
        stu.branch = request.form.get("branch")
        stu.phone = request.form.get("phone")
        stu.cgpa = request.form.get("cgpa")

        email = request.form.get("email")
        if email:
            stu.user.email = email

        file = request.files.get('resume')

        if file and file.filename != '':
            if allowed_file(file.filename):

                upload_folder = os.path.join('app', 'static', 'uploads')

                filename = secure_filename(file.filename)
                filename = f"resume_{stu.id}_{filename}"

                file.save(os.path.join(upload_folder, filename))
                stu.resume = filename

            else:
                flash("Invalid file type!", "danger")
                return redirect(request.url)

        db.session.commit()
        flash("Profile updated!", "success")

        return redirect(url_for('student.stu_profile', id=stu.id))

    return render_template("student/profile.html", curr_student=stu)


@student.route('/student/organisation')
@login_required
def organization():

    stu = student_required()

    today = date.today()

    drives = PlacementDrive.query.filter(
        PlacementDrive.status == "open",
        PlacementDrive.deadline >= today )

    companies = []
    seen = set()

    for d in drives:
        if d.company_id not in seen:
            companies.append(d.company)  
            seen.add(d.company_id)

    return render_template(
        "student/organisation.html",
        companies=companies
    )
# Applications 
@student.route('/student/application')
@login_required
def application():

    stu = student_required()

    search = request.args.get("search", "")

    query = Application.query.join(PlacementDrive).filter(
        Application.student_id == stu.id
    )

    if search:
        query = query.filter(
            PlacementDrive.job_title.ilike(f"%{search}%")
        )

    myapp = query.all()

    return render_template(
        'student/application.html',
        myapp=myapp,
        stu=stu
    )


@student.route('/student/history')
@login_required
def history():

    stu = student_required()

    # get all applications of student
    myapp = Application.query.filter_by(student_id=stu.id)\
                             .order_by(Application.id.desc())\
                             .all()

    return render_template(
        'student/history.html',  
        myapp=myapp,
        stu=stu
    )

@student.route('/student/company/<int:company_id>')
@login_required
def company_drives(company_id):

    stu = student_required()
    today = date.today()

    company = Company.query.get_or_404(company_id)

    drives = PlacementDrive.query.filter(
        PlacementDrive.company_id == company_id,
        PlacementDrive.status == "open",
        PlacementDrive.deadline >= today
    ).all()

    applied_ids = [a.drive_id for a in Application.query.filter_by(student_id=stu.id)]

    return render_template(
        'student/company_drives.html',
        company=company,
        drives=drives,
        applied_drive_ids=applied_ids
    )