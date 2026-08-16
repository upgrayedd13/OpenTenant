#from apscheduler.schedulers.background import BackgroundScheduler
from time import sleep, perf_counter
from pathlib import Path
import logging.config

from ..scrapers.fetch_available_apartments import get_apartment_snapshot
from ..logging_config import LOGGING_CONFIG

#from .registry import load_jobs_from_db
from .db import SessionLocal

PERIOD_HOURS = 12
PERIOD_SECONDS = PERIOD_HOURS * 3600
HEARTBEAT_INTERVAL_SECONDS = 30
HEALTH_FILE = Path('/tmp/scheduler-health')


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('scheduler.runner')
# scheduler = BackgroundScheduler()


def get_apartments() -> None:
    logger.info('Fetching apartment data...')

    # get the apartment data
    t0 = perf_counter()
    data = get_apartment_snapshot()
    t1 = perf_counter()
    logger.info(f'Fetching apartment data took {t1 - t0:.2f} seconds')

    # commit the data to the DB
    with SessionLocal() as session:
        session.add(data)
        session.commit()


def update_health(success: bool) -> None:
    HEALTH_FILE.write_text('1' if success else '0')


# TODO: make this more dynamic (for now, the simplicity is all we need)
def main() -> None:
    logger.info('Scheduler running')
    #load_jobs_from_db(scheduler)
    #scheduler.start()

    # event loop
    while True:
        # perform the task
        try:
            get_apartments()
            success = True
        except Exception as e:
            logger.exception(f'Failed to fetch apartment data!')
            logger.exception(e)
            success = False

        # wait for some period of time before running again
        logger.info(f'Sleeping for {PERIOD_HOURS} hours ({PERIOD_SECONDS} seconds)...')
        for _ in range(0, PERIOD_SECONDS, HEARTBEAT_INTERVAL_SECONDS):
            update_health(success)
            sleep(HEARTBEAT_INTERVAL_SECONDS)


if __name__ == '__main__':
    main()
