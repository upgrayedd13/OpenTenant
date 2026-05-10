from flask import Blueprint, render_template
import logging


about_bp = Blueprint('about', __name__, url_prefix='/about', template_folder='templates', static_folder='static', static_url_path='/about/static')
logger = logging.getLogger(__name__)


@about_bp.route('/calendar')
def calendar() -> None:
    return render_template('about/calendar.html')


@about_bp.route('/bylaws')
def bylaws() -> None:
    return render_template('about/bylaws.html')


@about_bp.route('/who_we_are')
def who_we_are() -> None:
    return render_template('about/who_we_are.html')
