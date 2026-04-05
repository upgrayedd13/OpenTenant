from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from pprint import pprint
import os

from ..utils.rand_string import genRandomString
from ..parsers.leaseParser import parse_lease
from ..utils.get_config import get_config
from ..models.emergency_contact import EmergencyContact
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
        ec: EmergencyContact = form.emergency_contact.create_emergency_contact()
        l: Lease = form.apartment_info.create_lease()

        # fill in the username and password
        user.username = form.register_info.username.data
        user.set_password(form.register_info.password.data)

        # link the user and emergency contact
        user.emergency_contact = ec
        user.leases.append(l)

        # add everything to the database
        db.session.add(user)
        db.session.commit()

        # take the user to the login page
        flash('Account created! Please log in.')
        return redirect(url_for('account.login'))

    for dict in form.errors.values():
        for errors in dict.values():
            for error in errors:
                flash(error)
    return render_template('pages/register.html', form=form)


# TODO: add a loading icon while lease is being parsed
@account_bp.route('/upload-lease', methods=['POST'])
def upload_lease():
    # get the file
    file = request.files.get('pdf')
    if not file:
        return jsonify({'error': 'No file'}), 400

    # check that the filename wasn't maliciously formed and complain about it if it was
    fname = secure_filename(file.filename)
    if fname != file.filename:
        return jsonify({'error': 'Got malicious filename! This will be logged'}), 400

    # ensure it's a PDF
    if os.path.splitext(fname)[1] != '.pdf':
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    # add a random string of characters to ensure it's unique
    fname = genRandomString(8) + fname

    # write the file to disk
    full_file_path = os.path.join(get_config('LEASES_DIR'), fname)
    file.save(full_file_path)

    # parse the file
    parsed_data = parse_lease(full_file_path)
    return jsonify(parsed_data)


@account_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('account.login'))


@account_bp.route("/account")
@login_required
def account():
    form = SignupForm()
    return render_template("pages/account.html", user=current_user, form=form)
