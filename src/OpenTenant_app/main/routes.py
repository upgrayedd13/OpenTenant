from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static', static_url_path='/main/static')


@main_bp.route('/')
def homepage():
    return render_template('main/index.html')


@main_bp.route('/bug')
def bug():
    return render_template('main/bug_report.html')
