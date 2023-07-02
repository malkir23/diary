from celery import Celery
from celery.utils.log import get_task_logger
from celery.schedules import crontab
from app.services.scraping import generate_random_data, get_data_from_api
from app.settings.config import settings

celery_instance = Celery("tasks", broker="redis://redis:6379/0")

logger = get_task_logger(__name__)

CELERY_TEST_ENV = settings.CELERY_TEST_ENV


@celery_instance.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    if not CELERY_TEST_ENV:
        # weekly task
        sender.add_periodic_task(
            crontab(hour=7, minute=30, day_of_week=1),  # weekly
            periodicity_task.s(period="w"),
        )
        # daily task
        sender.add_periodic_task(
            crontab(minute=0, hour=0),  # daily
            periodicity_task.s(period="d"),
        )
        # monthly task
        sender.add_periodic_task(
            crontab(0, 0, day_of_month="1"),  # monthly
            periodicity_task.s(period="m"),
        )


@celery_instance.task
def task_1(param):
    logger.info(f"ping {param}")
    generate_random_data()


@celery_instance.task
def periodicity_task(period):
    get_data_from_api(period=period)


"""
1) celery -A tasks beat --loglevel=INFO
2) celery -A tasks worker --loglevel=INFO -P threads
"""
