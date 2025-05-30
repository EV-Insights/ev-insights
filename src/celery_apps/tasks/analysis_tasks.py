from src.celery_apps.worker import celery_app
from src.__main__ import main


@celery_app.task(bind=True, queue='stats_queue')
def stats_task(self, config: dict):
    output = main(config_json=config)
    return {'message': output}
