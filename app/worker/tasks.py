from celery import Celery
from celery.schedules import crontab
from app.parsers.fomenki_parser_main import get_main_data
from app.parsers.fomenki_parser_detail import fomenki_parser_detail
from app.parsers.fomenki_parser_critical_afishas import fomenki_parser_critical_afishas
from celery import chain

celery_app = Celery('app')
celery_app.config_from_object('app.config')

@celery_app.task
def scheduled_parsing_main(*args, **kwargs):
    get_main_data()

# @celery_app.task
# def scheduled_parsing_detail(*args, **kwargs):
#     fomenki_parser_detail()
#
# @celery_app.task
# def scheduled_parsing_critical(*args, **kwargs):
#     fomenki_parser_critical_afishas()
#
# @celery_app.task
# def scheduled_parsing(*args, **kwargs):
#     task_chain = chain(scheduled_parsing_main.s(), scheduled_parsing_detail.s(), scheduled_parsing_critical.s())
#     task_chain()

celery_app.conf.beat_schedule = {
    "run-update-spectacles": {
        "task": "app.worker.tasks.scheduled_parsing_main",
        "schedule": crontab(minute=0, second=30),
    }
}
