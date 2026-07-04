from time import sleep

from src.OpenTenant_app import create_app
from src.OpenTenant_app.scheduler.service import start_scheduler

app = create_app()

if __name__ == '__main__':
    start_scheduler(app)

    # keep process alive
    while True:
        sleep(3600)