from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, login_user, logout_user, current_user

from ..models.user import User
from ..extensions import db

from .forms import LoginForm, RegisterForm

account_bp = Blueprint('account', __name__)

@account_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user: User = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            remember = request.form.get('remember') == 'on'  # True if checkbox checked
            login_user(user, remember=remember)  # <-- remember=True keeps session across browser restarts
            return redirect(url_for('account.account'))
        flash('Invalid credentials')
    return render_template('pages/login.html', form=form)


@account_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists')
            return redirect(url_for('register'))

        user = User(username=form.username.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Account created. Please log in.')
        return redirect(url_for('login'))

    return render_template('pages/register.html', form=form)


@account_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('account.login'))


@account_bp.route("/parse-lease", methods=["POST"])
@login_required
def parse_lease():
    file = request.files.get("pdf")
    if not file:
        return jsonify({"error": "No file"}), 400

    parsed_data = parse_lease(file)
    return jsonify(parsed_data)


@account_bp.route("/account")
@login_required
def account():
    return render_template("pages/account.html", user=current_user)
