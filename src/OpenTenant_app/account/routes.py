from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, login_user, logout_user, current_user
from pprint import pprint

from ..parsers.leaseParser import parse_lease
from ..models.lease import Lease
from ..models.user import User
from ..extensions import db

from .forms import LoginForm, SignupForm

account_bp = Blueprint('account', __name__)

@account_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user: User = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            remember = request.form.get('remember') == 'on'  # True if checkbox checked
            login_user(user, remember=remember)              # remember=True keeps session across browser restarts
            return redirect(url_for('account.account'))
        flash('Invalid credentials')
    return render_template('pages/login.html', form=form)


@account_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = SignupForm()

    if form.validate_on_submit():
        # create the objects
        user: User = form.personal_info.create_user()
        l: Lease = form.apartment_info.create_lease()

        # fill in the username and password
        user.username = form.register_info.username.data
        user.set_password(form.register_info.password.data)

        # add everything to the database
        db.session.add(user)
        db.session.commit()

        # take the user to the login page
        flash('Account created! Please log in.')
        return redirect(url_for('account.login'))

    pprint(form.errors)
    return render_template('pages/register.html', form=form)


@account_bp.route("/upload-lease", methods=["POST"])
def upload_lease():
    file = request.files.get("pdf")
    if not file:
        return jsonify({"error": "No file"}), 400

    # TODO: add a loading icon while lease is being parsed
    parsed_data = parse_lease(file)
    return jsonify(parsed_data)


@account_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('account.login'))


@account_bp.route("/account")
@login_required
def account():
    user: User = User.query.filter_by(username=current_user.username).one()
    form = SignupForm.from_user(user)
    return render_template("pages/account.html", user=current_user, form=form)
