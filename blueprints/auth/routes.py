from datetime import datetime
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user

from extensions import db
from forms import LoginForm, RegisterForm
from models import User, Company
from blueprints.auth import auth_bp


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash("That email is already registered.", "danger")
            return render_template("auth/register.html", form=form)

        company = Company(name=form.company_name.data.strip(),
                          phone=form.phone.data, email=form.email.data.lower())
        db.session.add(company)
        db.session.flush()

        user = User(company_id=company.id, email=form.email.data.lower(),
                    full_name=form.full_name.data.strip(),
                    phone=form.phone.data, role="admin")
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if not user or not user.check_password(form.password.data) or not user.is_active:
            flash("Invalid credentials.", "danger")
            return render_template("auth/login.html", form=form)
        login_user(user, remember=True)
        user.last_login = datetime.utcnow()
        db.session.commit()
        return redirect(request.args.get("next") or url_for("dashboard.index"))
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))