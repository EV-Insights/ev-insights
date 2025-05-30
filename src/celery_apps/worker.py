from celery import Celery
import os
import multiprocessing
import subprocess
# multiprocessing.set_start_method('fork')


celery_app = Celery(
    'worker',
    broker='redis://127.0.0.1:6379/0',
    backend='redis://127.0.0.1:6379/0',
    include=["src.celery_apps.tasks.admin_tasks",
             "src.celery_apps.tasks.analysis_tasks",
             "src.celery_apps.tasks.forecast_tasks",
             "src.celery_apps.tasks.ingestion_tasks"],
)

celery_app.conf.update(
    worker_log_level='INFO',
    broker_transport_options={'visibility_timeout': int(os.getenv("CELERY_VISIBILITY_TIMEOUT", 43200))}
)


# def start_flower():
#     command = [
#         'celery',
#         '-A',
#         'src.celery_apps.worker',
#         'flower',
#         '--port=5555',
#         '--address=0.0.0.0',
#         '--loglevel=info'
#     ]
# 
#     process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#
#     return process
#
#
# # Start Flower
# flower_process = start_flower()
