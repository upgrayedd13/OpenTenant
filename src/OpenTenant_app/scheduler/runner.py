#from apscheduler.schedulers.background import BackgroundScheduler
from time import sleep, perf_counter
import logging

from ..scrapers.fetch_available_apartments import get_apartment_snapshot

#from .registry import load_jobs_from_db
from .db import SessionLocal

PERIOD_HOURS = 12
PERIOD_SECONDS = PERIOD_HOURS * 3600

logger = logging.getLogger(__name__)
# scheduler = BackgroundScheduler()


def get_apartments() -> None:
    logger.log('Fetching apartment data...')
    
    # get the apartment data
    t0 = perf_counter()
    data = get_apartment_snapshot()
    t1 = perf_counter()
    logger.log(f'Fetching apartment data took {t1 - t0:.2f} seconds')

    # commit the data to the DB
    with SessionLocal() as session:
        session.add(data)
        session.commit()


def main() -> None:
    logger.log('Scheduler running')
    #load_jobs_from_db(scheduler)
    #scheduler.start()

    # event loop
    while True:
        # perform the task
        try:
            get_apartments()
        except Exception as e:
            logger.exception(f'Failed to fetch apartment data!')
            logger.exception(e)

        # wait for some period of time before running again
        logger.log(f'Sleeping for {PERIOD_HOURS} hours ({PERIOD_SECONDS} seconds)...')
        sleep(PERIOD_SECONDS)


if __name__ == '__main__':
    main()
