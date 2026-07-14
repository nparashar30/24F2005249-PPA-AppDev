import os
import csv
from datetime import datetime, timezone, timedelta
from celery import Celery
from celery.schedules import crontab
from config import Config

celery = Celery('placement_portal')
celery.conf.update(
    broker_url=Config.CELERY_BROKER_URL,
    result_backend=Config.CELERY_RESULT_BACKEND,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
    beat_schedule={
        'daily-deadline-reminders': {
            'task': 'tasks.scheduled_tasks.send_daily_deadline_reminders',
            'schedule': crontab(hour=9, minute=0),
        },
        'monthly-admin-report': {
            'task': 'tasks.scheduled_tasks.send_monthly_admin_report',
            'schedule': crontab(day_of_month=1, hour=8, minute=0),
        },
        'daily-interview-reminders': {
            'task': 'tasks.scheduled_tasks.send_interview_reminders',
            'schedule': crontab(hour=8, minute=30),
        },
    },
)

celery.autodiscover_tasks(['tasks'])
