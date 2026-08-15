from flask import Blueprint, Response, render_template, abort, url_for
from jinja2.exceptions import TemplateNotFound
import logging

from .seo_lists import ROBOTS_DISALLOW_LIST, SITEMAP_ENDPOINTS


main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static', static_url_path='/main/static')
logger = logging.getLogger(__name__)


@main_bp.route('/')
def homepage():
    return render_template('main/index.html')


@main_bp.route('/modal/<name>')
def modal_content(name: str):
    try:
        return render_template(f'modals/{name}.html')
    except TemplateNotFound:
        abort(404)


@main_bp.route('/robots.txt')
def robots() -> Response:
    content = [
        'User-agent: *',
        *[f'Disallow: {endpoint}' for endpoint in ROBOTS_DISALLOW_LIST],
        'Sitemap: https://lpmtu.com/sitemap.xml',
    ]
    return Response('\n'.join(content) + '\n', mimetype='text/plain')


@main_bp.route('/sitemap.xml')
def sitemap() -> Response:
    urls = sorted(url_for(endpoint, _external=True) for endpoint in SITEMAP_ENDPOINTS)
    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        *[f'    <url><loc>{url}</loc></url>' for url in urls],
        '</urlset>',
    ]
    return Response('\n'.join(xml) + '\n', mimetype='application/xml')
