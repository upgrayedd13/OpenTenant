from flask import Blueprint, render_template, abort
import logging


main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static', static_url_path='/main/static')
logger = logging.getLogger(__name__)


@main_bp.route('/')
def homepage():
    return render_template('main/index.html')


@main_bp.route('/modal/<name>')
def modal_content(name: str):
    try:
        return render_template(f'modals/{name}.html')
    except:
        abort(404)
