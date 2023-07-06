from celery import Celery
from celery.utils.log import get_task_logger
from celery.schedules import crontab
from backend.services.scraping import Scraping
from backend.settings.config import settings

celery_instance = Celery("tasks", broker="redis://redis:6379/0")

logger = get_task_logger(__name__)

CELERY_TEST_ENV = settings.CELERY_TEST_ENV


@celery_instance.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
        # weekly task
    sender.add_periodic_task(
        crontab(hour=10, minute=0, day_of_week=1),  # weekly   crontab(hour=9, minute=0, day_of_week=1) > Every Monday  6:00 AM from EST
        periodicity_task.s(period="w"),
    )
        # daily task
    sender.add_periodic_task(
        crontab(minute=0, hour=10),  # crontab(minute=0, hour=9) -> daily 6:00 AM from EST (13:00  in UA)
        periodicity_task.s(period="d"),
    )
        # monthly task
    sender.add_periodic_task(
        crontab(0, 0, day_of_month="1"),  # monthly
        periodicity_task.s(period="m"),
    )

@celery_instance.task
def periodicity_task(period):
    scraping = Scraping()
    scraping.get_data(period=period)


"""
1) celery -A tasks beat --loglevel=INFO
2) celery -A tasks worker --loglevel=INFO -P threads
"""
