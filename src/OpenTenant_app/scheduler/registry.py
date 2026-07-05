from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import sys

from ..models.scheduled_job import ScheduledJob
from .jobs import function_map
from .db import SessionLocal


def load_jobs_from_db(scheduler: BackgroundScheduler) -> None:
    session = SessionLocal()
    jobs: list[ScheduledJob] = session.query(ScheduledJob).filter_by(enabled=True).all()

    if len(jobs) == 0:
        print('Didn\'t get any jobs!', file=sys.stderr)

    for job in jobs:
        if job.function not in function_map:
            print(f'Found job with function "{job.function}", but that isn\'t a registered function!', file=sys.stderr)
            continue

        name = job.name
        func = job.function

        print(f'Got job {name}, which will call {func} at {job.minute} {job.hour} {job.dom} {job.month} {job.dow}')

        scheduler.add_job(
            func=function_map[func],
            trigger=CronTrigger(
                minute=job.minute,
                hour=job.hour,
                day=job.dom,
                month=job.month,
                day_of_week=job.dow,
            ),
            id=name,
            replace_existing=True,
        )

    session.close()
