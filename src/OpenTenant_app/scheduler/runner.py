from apscheduler.schedulers.background import BackgroundScheduler
from time import sleep

from .registry import load_jobs_from_db


scheduler = BackgroundScheduler()


def main():
    print('Scheduler running')
    load_jobs_from_db(scheduler)
    scheduler.start()

    while True:
        sleep(3600)


if __name__ == '__main__':
    main()
