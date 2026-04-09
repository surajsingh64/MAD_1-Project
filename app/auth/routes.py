from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import Student, User, Company
from . import auth_bp

# Student Register
@auth_bp.route("/register/student", methods=["GET", "POST"])
def register_student():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")
        roll_no = request.form.get("roll_no")

        if User.query.filter_by(email=email).first():
            flash("Already registered")
            return redirect(url_for("auth_bp.login"))

        user = User(
        email=email,
        password=generate_password_hash(password),
        role="student"
    )

        db.session.add(user)
        db.session.flush()   # gets user.id without committing

        student = Student(
        user_id=user.id,
        name=name,
        roll_no=roll_no
    )

        db.session.add(student)
        db.session.commit()

        flash("Registered successfully, please login.")
        return redirect(url_for("auth_bp.login"))

    return render_template("auth/register_student.html")

# Company Register

@auth_bp.route("/register/company", methods=["GET", "POST"])
def register_company():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")
        company_name = request.form.get("company_name")

        if User.query.filter_by(email=email).first():
            flash("Company already registered")
            return redirect(url_for("auth_bp.login"))

        user = User(
            email=email,
            password=generate_password_hash(password),
            role="company"
        )

        db.session.add(user)
        db.session.flush()  

        company = Company(
            user_id=user.id,
            company_name=company_name
        )

        db.session.add(company)
        db.session.commit()

        flash("Registered successfully, please login.")
        return redirect(url_for("auth_bp.login"))

    return render_template("auth/register_company.html")


# Login

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            if user.role == "admin":
                return redirect(url_for("admin.a_admin"))

            elif user.role == "student":
                return redirect(url_for("student.dashboard"))

            else:
                return redirect(url_for("company.company_dashboard"))

        flash("Invalid email or password!")

    return render_template("auth/login.html")


# -----------------------------
# Logout
# -----------------------------
@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()
    return redirect(url_for("auth_bp.login"))