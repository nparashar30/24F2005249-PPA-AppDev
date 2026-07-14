"""Initialize database and seed default admin user programmatically."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db
from models.models import User
from config import Config


def init_database():
    app = create_app()
    with app.app_context():
        db.create_all()
        print('Database tables created successfully.')

        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                email=Config.ADMIN_EMAIL,
                role='admin',
                is_active=True,
            )
            admin.set_password(Config.ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()
            print(f'Admin user created: {Config.ADMIN_EMAIL}')
        else:
            print(f'Admin user already exists: {admin.email}')

        print('\n--- Database ready ---')
        print(f'Admin login: {Config.ADMIN_EMAIL} / {Config.ADMIN_PASSWORD}')


if __name__ == '__main__':
    init_database()
