from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from shutil import move
import logging
import uuid
import os

from ..parsers.leaseParser import parse_lease
from ..utils.get_config import get_config
from ..models.lease import Lease
from ..models.user import User
from ..extensions import db

from .forms import LoginForm, SignupForm


account_bp = Blueprint('account', __name__, url_prefix='/account', template_folder='templates', static_folder='static', static_url_path='/account/static')
logger = logging.getLogger(__name__)


@account_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_one_or_none_by(username=form.username.data)
        if user and user.check_password(form.password.data or ''):
            remember = request.form.get('remember') == 'y'
            login_user(user, remember=remember)
            return redirect(url_for('account.account'))
        flash('Invalid credentials')
    return render_template('account/login.html', form=form)


@account_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = SignupForm()

    if form.validate_on_submit():
        # create the objects
        # because the subforms are technically FlaskForms, tell Pylance to ignore the type and trust us
        user: User = form.personal_info.create_user()  # type: ignore
        l: Lease = form.apartment_info.create_lease()  # type: ignore

        # fill in the username and password
        user.username = form.register_info.username.data or ""
        user.set_password(form.register_info.password.data or "")

        # TODO: make sure there's enough space for this file

        # move the file to the actual upload directory
        token = form.register_info.upload_token.data or ""
        tmp_path = os.path.join(get_config('TMP_DIR'), token)
        real_path = os.path.join(get_config('LEASES_DIR'), token)
        move(tmp_path, real_path)

        # add the path to the lease
        l.path = real_path

        # link the user and emergency contact
        user.leases.append(l)

        # add everything to the database
        db.session.add(user)
        db.session.commit()

        # take the user to the login page
        flash('Account created! Please log in.')
        return redirect(url_for('account.login'))

    # flash errors to the user
    for errors in form.errors.values():
        for error in errors:
            flash(error)

    return render_template('account/register.html', form=form)


@account_bp.route('/upload-lease', methods=['POST'])
def upload_lease():
    # get the file
    file = request.files.get('pdf')
    if file is None or not file or file.filename is None:
        return jsonify({'error': "Didn't get a file!"}), 400

    # secure_filename will replace spaces with _ so we'll prematurely
    # perform that replacement for comparison later so files that have
    # spaces aren't marked as malicious
    no_space_fname = file.filename.replace(' ', '_')

    # check that the filename wasn't maliciously formed and complain about it if it was
    fname = secure_filename(no_space_fname)
    if fname != no_space_fname:
        return jsonify({'error': 'Got malicious filename! This will be logged!'}), 400

    # ensure it's a PDF
    if os.path.splitext(fname)[1] != '.pdf':
        return jsonify({'error': 'Only PDF files are allowed!'}), 400

    # add a random string of characters to ensure it's unique
    hex_string = uuid.uuid4().hex
    fname = f'{hex_string}_{fname}'

    # make sure the filename isn't too long
    tmp_path = get_config('TMP_DIR')
    if len(fname) > os.pathconf(tmp_path, 'PC_NAME_MAX'):
        return jsonify({'error': f'Name "{file.filename}" exceeds maximum filename size!'}), 400

    # TODO: make sure there's enough space for this file

    # write the file to disk
    full_file_path = os.path.join(tmp_path, fname)
    file.save(full_file_path)

    # parse the file
    parsed_data = parse_lease(full_file_path)
    parsed_data['upload_token'] = fname
    return jsonify(parsed_data)


@account_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('account.login'))


@account_bp.route('/account')
@login_required
def account():
    user = current_user._get_current_object()
    if user is None:
        return redirect(url_for('account.login'))
    form = SignupForm.from_user(user)
    form.disable_editing()
    return render_template('account/account.html', user=current_user, form=form)
