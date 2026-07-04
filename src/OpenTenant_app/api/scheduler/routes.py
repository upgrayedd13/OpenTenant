from flask import Blueprint, request, current_app

from src.OpenTenant_app.extensions import db
from src.OpenTenant_app.jobs.daily import run_daily_job
from src.OpenTenant_app.models.scheduled_job import ScheduledJob
from src.OpenTenant_app.scheduler.service import reload_scheduler

bp = Blueprint('scheduler', __name__, url_prefix='/api/scheduler')


@bp.route('/job/<name>', methods=['POST'])
def update_job(name):
    data = request.json

    job = ScheduledJob.query.filter_by(name=name).first_or_404()

    job.minute = data['minute']
    job.hour = data['hour']
    job.dom = data['dom']
    job.month = data['month']
    job.dow = data['dow']

    job.enabled = data.get('enabled', True)

    db.session.commit()

    reload_scheduler(current_app)

    return {'status': 'updated'}


@bp.route('/job/<name>/run', methods=['POST'])
def run_job_now(name):
    run_daily_job()
    return {'status': 'executed'}