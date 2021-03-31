from flask import Blueprint, render_template, url_for, flash, redirect, request
from tdee_app.models import User
from tdee_app import db, bcrypt
from tdee_app.users.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flask_login import login_user, current_user, logout_user, login_required

users = Blueprint('users', __name__)


@users.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password, start_weight=form.start_weight.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account Created For {form.username.data}.', category='success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Incorrect credentials', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route('/logout', methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.start_date = form.start_date.data
        current_user.start_weight = form.start_weight.data
        db.session.commit()
        flash('Account Updated.', 'success')
        return redirect(url_for('users.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.start_date.data = current_user.start_date
        form.start_weight.data = current_user.start_weight
        
    return render_template('profile.html', title='Profile', form=form)
