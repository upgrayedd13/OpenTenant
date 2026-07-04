from apscheduler.triggers.cron import CronTrigger

from scrapers.fetch_available_apartments import run_daily_job
from models.scheduled_job import ScheduledJob


def load_jobs_from_db(scheduler, app):
    jobs = ScheduledJob.query.filter_by(enabled=True).all()

    for job in jobs:
        scheduler.add_job(
            func=run_daily_job,
            trigger=CronTrigger(
                minute=job.minute,
                hour=job.hour,
                day=job.dom,
                month=job.month,
                day_of_week=job.dow,
            ),
            id=job.name,
            replace_existing=True,
        )