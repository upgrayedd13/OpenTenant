from apscheduler.schedulers.background import BackgroundScheduler
from src.OpenTenant_app.scheduler.registry import load_jobs_from_db

scheduler = BackgroundScheduler()


def start_scheduler(app):
    with app.app_context():
        load_jobs_from_db(scheduler, app)

    scheduler.start()


def reload_scheduler(app):
    with app.app_context():
        scheduler.remove_all_jobs()
        load_jobs_from_db(scheduler, app)