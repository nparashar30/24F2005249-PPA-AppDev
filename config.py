import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-dev-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'placement_portal.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')

    CACHE_DEFAULT_TTL = int(os.getenv('CACHE_DEFAULT_TTL', 300))

    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@institute.edu')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_FROM = os.getenv('MAIL_FROM', 'noreply@placementportal.edu')
    ADMIN_REPORT_EMAIL = os.getenv('ADMIN_REPORT_EMAIL', 'admin@institute.edu')
    GCHAT_WEBHOOK_URL = os.getenv('GCHAT_WEBHOOK_URL', '')

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    EXPORT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
