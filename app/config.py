from celery import Celery

celery_app = Celery('app')
celery_app.config_from_object('app.config')

celery_app.conf.broker_url = 'redis://redis:6379/0'
celery_app.conf.result_backend = 'redis://redis:6379/0'
celery_app.conf.timezone = 'UTC'