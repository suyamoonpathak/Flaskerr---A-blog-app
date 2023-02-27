from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re

authentication = Blueprint("authentication", __name__)


@authentication.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@authentication.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        pwd = request.form.get("pwd")
        pwdConfirm = request.form.get("pwdConfirm")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash(
                'This email has already been chosen, please choose another one.', category='error')
        elif username_exists:
            flash(
                'This username has already been chosen, please choose another one.', category='error')
        elif pwd != pwdConfirm:
            flash('Please type the same passwords', category='error')
        elif len(username) < 4:
            flash('Please choose a longer username. Username length should be greater than 3 letters.', category='error')
        elif len(pwd) < 4:
            flash('Please choose a longer password. Username length should be greater than 3 letters.', category='error')
        elif not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email):
            flash("Please choose a valid email.", category='error')
        else:
            newUser = User(email=email, username=username, password=generate_password_hash(
                pwd, method='sha256'))
            db.session.add(newUser)
            db.session.commit()
            login_user(newUser, remember=True)
            flash('User created!')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)


@authentication.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))
