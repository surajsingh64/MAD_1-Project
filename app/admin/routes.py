from flask import render_template, abort, url_for, redirect, flash, request
from flask_login import login_required, current_user
from . import admin_bp as admin
from app.models import Student, Company, PlacementDrive, Application, User
from app import db
from sqlalchemy import or_
from datetime import date


#admin checking 
def admin_required():
    if current_user.role != "admin":
        flash("Access denied!", "danger")
        return False
    return True


# Dashboard 
@admin.route('/dashboard')
@login_required
def a_admin():

    if not admin_required():
        return redirect(url_for("auth.login"))

    stats = {
        "total_student": Student.query.count(),
        "total_companies": Company.query.count(),
        "total_drives": PlacementDrive.query.count(),
        "total_applications": Application.query.count()
    }

    # company filters
    company_data = {
        "blacklist_companies": Company.query.filter_by(approval_status='blacklisted').all(),
        "pending_companies": Company.query.filter_by(approval_status='pending').all(),
        "rejected_companies":Company.query.filter_by(approval_status='rejected').all(),
    }
    company_data["all_blocked_companies"] = company_data["blacklist_companies"]

    # drive filters
    drive_data = {
        "pending_drives": PlacementDrive.query.filter_by(status='pending').all(),
        "reject_drives": PlacementDrive.query.filter_by(status='rejected').all()
    }

    # application stats
    app_stats = {
        "status_applied": Application.query.filter_by(status='applied').count(),
        "status_shortlisted": Application.query.filter_by(status='shortlisted').count(),
        "status_selected": Application.query.filter_by(status='selected').count(),
        "status_rejected": Application.query.filter_by(status='rejected').count()
    }

    # drive stats
    drive_stats = {
        "drives_pending": PlacementDrive.query.filter_by(status='pending').count(),
        "drives_open": PlacementDrive.query.filter_by(status='open').count(),
        "drives_rejected": PlacementDrive.query.filter_by(status='rejected').count(),
        "drives_closed": PlacementDrive.query.filter_by(status='closed').count()
    }

    return render_template(
        'admin/dashboard.html',
        **stats,
        **company_data,
        **drive_data,
        **app_stats,
        **drive_stats,
        view=request.args.get("view"),
        drive_view=request.args.get("drive_view")
    )


# Generic Company Status Update
def update_company_status(id, status):
    company = Company.query.get_or_404(id)
    company.approval_status = status
    db.session.commit()
    flash(f"Company marked as {status}", "info")

@admin.route('/approve/<int:id>')
@login_required
def approve_company(id):
    if not admin_required():
        return redirect(url_for("auth.login"))
    update_company_status(id, "approved")
    return redirect(url_for('admin.companies'))


@admin.route('/reject/<int:id>')
@login_required
def reject_company(id):
    if not admin_required():
        return redirect(url_for("auth.login"))
    update_company_status(id, "rejected")
    return redirect(url_for('admin.companies'))


@admin.route('/blacklist/<int:id>')
@login_required
def blacklist_company(id):
    if not admin_required():
        return redirect(url_for("auth.login"))
    update_company_status(id, "blacklisted")
    return redirect(url_for('admin.companies'))

@admin.route('/whitelist/<int:id>')
@login_required
def whitelist_company(id):
    if not admin_required():
        return redirect(url_for("auth.login"))
    update_company_status(id, "approved")
    return redirect(url_for('admin.companies'))

# Generic Drive Status Update
def update_drive_status(id, status):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = status
    db.session.commit()
    flash(f"Drive marked as {status}", "info")


@admin.route('/approve_drives/<int:id>')
@login_required
def approve_drives(id):
    if not admin_required():
        return redirect(url_for("auth.login"))
    update_drive_status(id, "open")
    return redirect(url_for("admin.a_admin"))


@admin.route('/drives_reject/<int:id>')
@login_required
def reject_drives(id):
    if not admin_required():
        return redirect(url_for("auth.login"))
    update_drive_status(id, "rejected")
    return redirect(url_for("admin.a_admin"))


#  Companies navigator
@admin.route('/companies')
@login_required
def companies():

    if not admin_required():
        return redirect(url_for("auth.login"))

    search = request.args.get('search', '').strip()

    query = Company.query

    if search:
        query = query.filter(
            or_(
                Company.company_name.ilike(f"%{search}%"),
                Company.hr_name.ilike(f"%{search}%")
            )
        )
    companies = query.all()

    return render_template('admin/navigator/companies.html', companies=companies,search=search)


@admin.route('/edit_company/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_company(id):
    if not admin_required():
        return redirect(url_for("auth.login"))

    company = Company.query.get_or_404(id)

    if request.method == 'POST':
        company.company_name = request.form['company_name']
        company.hr_name = request.form['hr_name']
        company.website = request.form['website']
        db.session.commit()
        flash("Company updated successfully", "success")
        return redirect(url_for("admin.companies"))

    return render_template('admin/edit_company.html', company=company)


# Students
@admin.route('/students')
@login_required
def students():

    if not admin_required():
        return redirect(url_for("auth.login"))

    q = request.args.get('q', '').strip()

    query = Student.query.join(Student.user)

    if q:
        query = query.filter(
            or_(
                Student.name.ilike(f"%{q}%"),
                Student.roll_no.ilike(f"%{q}%"),
                User.email.ilike(f"%{q}%")
            )
        )

    students = query.all()
    return render_template('admin/navigator/students.html', students=students, q=q)


#  Student Blacklist
@admin.route('/deactivate_student/<int:id>')
@login_required
def deactivate_student(id):

    if not admin_required():
        return redirect(url_for("auth.login"))

    stu = Student.query.get_or_404(id)
    if stu.is_blacklisted == True :
         stu.is_blacklisted = False
    else :
         stu.is_blacklisted = True

    db.session.commit()
    flash("Student status updated", "success")
    return redirect(url_for("admin.students"))


@admin.route('/delete_student/<int:id>')
@login_required
def delete_student(id):
    if not admin_required():
        return redirect(url_for("auth.login"))

    student = Student.query.get_or_404(id)
    user = student.user
    db.session.delete(student)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash("Student and account deleted", "success")
    return redirect(url_for("admin.students"))

@admin.route('/toggle_blacklist/<int:id>')
@login_required
def toggle_blacklist(id):
    if not admin_required():
        return redirect(url_for("auth.login"))

    student = Student.query.filter_by(user_id=id).first_or_404()
    student.is_blacklisted = not student.is_blacklisted
    db.session.commit()
    flash("Student status updated", "success")
    return redirect(url_for("admin.students"))

@admin.route('/edit_student/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    if not admin_required():
        return redirect(url_for("auth.login"))

    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        student.name = request.form['name']
        student.roll_no = request.form['roll_no']
        student.branch = request.form['branch']
        student.cgpa = request.form.get('cgpa')
        student.phone = request.form['phone']
        db.session.commit()
        flash("Student updated successfully", "success")
        return redirect(url_for("admin.students"))

    return render_template('admin/edit_student.html', student=student)


# drives searching 
from datetime import date

@admin.route('/drives')
@login_required
def drives():

    if not admin_required():
        return redirect(url_for("auth.login"))

    search = request.args.get("search", "").strip()
    today = date.today()

    query = PlacementDrive.query.join(Company)

    if search:
        query = query.filter(
            or_(
                PlacementDrive.job_title.ilike(f"%{search}%"),
                Company.company_name.ilike(f"%{search}%")
            )
        )
    ongoing_drives = query.filter(PlacementDrive.deadline >= today).all()
    expired_drives = query.filter(PlacementDrive.deadline < today).all()

    return render_template(
        'admin/navigator/drives.html',
        ongoing_drives=ongoing_drives,
        expired_drives=expired_drives,
        search=search
    )
# Applicants 
@admin.route('/navigator/applications')
@login_required
def applications():

    if current_user.role != 'admin':
        abort(403)

    search = request.args.get("search", "")

    if search:
        applicants = Application.query.join(Student).join(PlacementDrive).join(Company).filter(
            or_(
                Student.name.like(f"%{search}%"),
                Student.roll_no.like(f"%{search}%"),
                PlacementDrive.job_title.like(f"%{search}%"),
                Company.company_name.like(f"%{search}%")
            )
        ).all()
    else:
        applicants = Application.query.all()

    return render_template(
        'admin/navigator/applications.html',
        applicants=applicants,   
        search=search         
    )
