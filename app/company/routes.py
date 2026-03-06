from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.admin.routes import drives
from app.models import Company, PlacementDrive, Application, Student
from . import company_bp
from datetime import datetime

from app import company

@company_bp.route("/dashboard")
@login_required
def company_dashboard():
    if current_user.role != "company":
        return "unauthorized", 403
    if not current_user.company:
    
        return "company profile not found", 404
    company = current_user.company
    drives=company.drives

    total_drives = len(drives)
    open_drives = len([d for d in drives if d.status == "open"])

    total_applications = sum(len(d.applications) for d in drives)
    return render_template(
            "company/dashboard.html",
            company=company,
            total_drives=total_drives,
            open_drives=open_drives,
            total_applications=total_applications
        )
 