from flask import Blueprint, render_template

resources_bp = Blueprint('resources', __name__, url_prefix='/resources', template_folder='templates', static_folder='static', static_url_path='/resources/static')


@resources_bp.route('/know_before_renting')
def know_before_renting() -> None:
    return render_template('resources/know_before_renting.html')


@resources_bp.route('/legal_resources')
def legal_resources() -> None:
    return render_template('resources/legal_resources.html')


@resources_bp.route('/useful_links')
def useful_links() -> None:
    return render_template('resources/useful_links.html')