from flask import Blueprint, render_template
import logging


main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static', static_url_path='/main/static')
logger = logging.getLogger(__name__)


@main_bp.route('/')
def homepage():
    return render_template('main/index.html')


@main_bp.route('/bug')
def bug():
    return render_template('main/bug_report.html')
