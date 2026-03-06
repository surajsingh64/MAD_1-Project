from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from . import auth_bp


# ---------------- REGISTER ----------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")  # student/admin/company

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists!")
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password)

        new_user = User(
            email=email,
            password=hashed_password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful!")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            # Role-based redirect
            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            elif user.role == "student":
                return redirect(url_for("student.dashboard"))
            else:
                return redirect(url_for("company.dashboard"))

        flash("Invalid email or password!")

    return render_template("auth/login.html")


# ---------------- LOGOUT ----------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
   # flash("Logged out successfully!")
    return redirect(url_for("auth.login"))