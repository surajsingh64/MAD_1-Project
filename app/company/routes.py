from datetime import datetime
from flask import render_template, abort, url_for, redirect, flash, request
from flask_login import login_required, current_user
from . import company_bp as company
from app.models import Company, PlacementDrive, Application
from app import db

def company_required():
    if current_user.role != "company":
        abort(403)
    if not current_user.company:
        abort(404)
    return current_user.company

# compnay Dashboard 
@company.route('/company_dashboard')
@login_required
def company_dashboard():

    comp = company_required()

    drives = PlacementDrive.query.filter_by(company_id=comp.id).all()

    total_drives = len(drives)
    open_drives = sum(1 for d in drives if d.status == 'open')
#total applicantion
    total_applications = sum(len(d.applications) for d in drives)
    return render_template(
        'company/company_dashboard.html',
        comp=comp,
        drives=drives,
        total_drives=total_drives,
        open_drives=open_drives,
        total_applications=total_applications
    )



@company.route('/create-drive', methods=['GET','POST'])
@login_required
def create_drive():

    comp = company_required()
    if comp.approval_status != 'approved' or comp.is_blacklisted:
        flash("Your account is not allowed to create drives.", "danger")
        return redirect(url_for("company.company_dashboard"))

    if request.method == 'POST':
        job_title = request.form.get("job_title")
        description = request.form.get("description")
        eligibility = request.form.get("eligibility")
        deadline_str = request.form.get("deadline")

        if not job_title or not deadline_str:
            flash("Please fill required fields", "danger")
            return redirect(request.url)

        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            if deadline < datetime.now():
                flash("Deadline must be in the future", "danger")
                return redirect(request.url)
        except ValueError:
            flash("Invalid date format", "danger")
            return redirect(request.url)

        new_drive = PlacementDrive(
            company_id=comp.id,
            job_title=job_title,
            description=description,
            eligibility=eligibility,
            deadline=deadline,
            status="pending"
        )

        db.session.add(new_drive)
        db.session.commit()

        flash("Drive Created Successfully!", "success")
        return redirect(url_for("company.company_dashboard"))
    
    return render_template("company/create_drive.html", comp=comp)

@company.route('/delete-drive/<int:id>', methods=['POST'])
@login_required
def delete_drive(id):

    comp = company_required()

    drive = PlacementDrive.query.get_or_404(id)

    if drive.company_id != comp.id:
        abort(403)

    if drive.applications:
        flash("Cannot delete drive with applications!", "warning")
        return redirect(url_for("company.company_dashboard"))

    db.session.delete(drive)
    db.session.commit()

    flash("Drive deleted successfully!", "success")
    return redirect(url_for("company.company_dashboard"))


# Edit Drive
@company.route('/edit-drive/<int:id>', methods=['POST','GET'])
@login_required
def edit_drive(id):

    comp = company_required()
    drive = PlacementDrive.query.get_or_404(id)

    if drive.company_id != comp.id:
        abort(403)

    if request.method == "POST":

        drive.job_title = request.form.get("job_title")
        drive.description = request.form.get("description")
        drive.eligibility = request.form.get("eligibility")

        deadline = request.form.get("deadline")
        if deadline:
            drive.deadline = datetime.strptime(deadline, "%Y-%m-%d")

        db.session.commit()
        flash("Drive updated", "success")

        return redirect(url_for("company.company_dashboard"))

    return render_template("company/edit_drive.html", curr_drive=drive)

@company.route('/company/drives')
@login_required
def placement_drives():

    comp = company_required()

    drives = PlacementDrive.query.filter_by(company_id=comp.id).all()

    return render_template(
        "company/placement_drives.html",
        drives=drives
    )


#  View Applications
@company.route('/view/<int:id>')
@login_required
def view_application(id):

    comp = company_required()
    drive = PlacementDrive.query.get_or_404(id)

    if drive.company_id != comp.id:
        abort(403)

    return render_template("company/view.html", drive=drive)


# Update Application Status 
@company.route("/company/update-status/<int:app_id>/<string:status>", methods=["POST"])
@login_required
def update_application_status(app_id, status):

    comp = company_required()

    app = Application.query.get_or_404(app_id)

    # Check if the application belongs to this company's drive
    if app.drive.company_id != comp.id:
        abort(403)

    if status not in ['applied', 'shortlisted', 'selected', 'rejected']:
        flash("Invalid status", "danger")
        return redirect(url_for('company.view_application', id=app.drive_id))

    app.status = status
    db.session.commit()

    flash(f"Application status updated to {status}", "success")
    return redirect(url_for('company.view_application', id=app.drive_id))

    comp = company_required()

    application = Application.query.get_or_404(app_id)

    if application.drive.company_id != comp.id:
        abort(403)

    valid_status = ["shortlisted", "selected", "rejected"]

    if status not in valid_status:
        abort(400)

    application.status = status
    db.session.commit()

    flash(f"Application marked as {status}", "success")

    return redirect(url_for("company.view_application", id=application.drive_id))


# Profile 
@company.route('/profile', methods=['GET','POST'])
@login_required
def profile():

    curr_company = Company.query.filter_by(user_id=current_user.id).first_or_404()

    if request.method == "POST":
        # curr_company.company_name = request.form.get("company_name")  # Readonly
        curr_company.hr_name = request.form.get("hr_name")
        curr_company.website = request.form.get("website")
        # curr_company.approval_status = request.form.get("approval_status")  # Readonly

        email = request.form.get("email")
        if email:
            curr_company.user.email = email

        db.session.commit()
        flash("Profile updated successfully!", "success")

        return redirect(url_for('company.profile'))

    return render_template("company/profile.html", curr_company=curr_company)