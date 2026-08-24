from flask import Blueprint, Response, render_template, abort, url_for, flash, current_app, request
from jinja2.exceptions import TemplateNotFound
from flask_mail import Message
import logging

from .seo_lists import ROBOTS_DISALLOW_LIST, SITEMAP_ENDPOINTS
from .forms import BugReportForm
from ..extensions import mail


main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static', static_url_path='/main/static')
logger = logging.getLogger(__name__)


@main_bp.route('/')
def homepage():
    return render_template('main/index.html')


@main_bp.route('/modal/bug_report', methods=['GET', 'POST'])
def bug_report_modal() -> str|tuple[str, int]|Response:
    MODAL_PATH = 'modals/bug_report.html'
    form = BugReportForm()

    if request.method == 'GET':
        return render_template(MODAL_PATH, form=form)

    if not form.validate_on_submit():
        return render_template(MODAL_PATH, form=form), 422

    name = form.name.data
    email = form.email.data
    description = form.description.data

    body = (
        'New Bug Report\n\n'
        f'Name:  {name}\n'
        f'Email: {email}\n\n'
        f'Description:\n{description}\n'
    )

    msg = Message(
        subject=f'Bug report from {name}',
        recipients=[current_app.config['BUG_REPORT_EMAIL']],
        reply_to=email,
        body=body,
    )

    mail.send(msg)

    flash('Bug report submitted successfully.', 'success')
    return Response(status=204)


@main_bp.route('/modal/<name>')
def modal_content(name: str) -> str:
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


@main_bp.route('/health')
def health() -> Response:
    return Response('OK', status=200)
