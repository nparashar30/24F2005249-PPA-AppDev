import os
import csv
from datetime import datetime, timezone
from celery_worker import celery


def _get_app_context():
    from app import create_app
    return create_app()


@celery.task(name='tasks.export_tasks.export_student_applications', bind=True)
def export_student_applications(self, student_id, email):
    app = _get_app_context()
    with app.app_context():
        from models.models import Student, Application
        from utils.notifications import send_email, send_gchat_message
        from config import Config

        student = Student.query.get(student_id)
        if not student:
            return {'error': 'Student not found'}

        apps = student.applications.order_by(Application.application_date.desc()).all()

        os.makedirs(Config.EXPORT_FOLDER, exist_ok=True)
        filename = f'applications_{student.student_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        filepath = os.path.join(Config.EXPORT_FOLDER, filename)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Student ID', 'Company Name', 'Drive Title',
                'Application Status', 'Application Date', 'Updated At',
            ])
            for a in apps:
                writer.writerow([
                    student.student_id,
                    a.job_position.company.company_name if a.job_position and a.job_position.company else '',
                    a.job_position.title if a.job_position else '',
                    a.status,
                    a.application_date.strftime('%Y-%m-%d') if a.application_date else '',
                    a.updated_at.strftime('%Y-%m-%d') if a.updated_at else '',
                ])

        subject = 'Your Application History Export is Ready'
        body = f'''
        <p>Hi {student.full_name},</p>
        <p>Your placement application history export has been completed.</p>
        <p>File: <strong>{filename}</strong></p>
        <p>Download it from your student dashboard.</p>
        '''
        send_email(email, subject, body)
        send_gchat_message(f'CSV export ready for {student.full_name}: {filename}')

        return {
            'status': 'complete',
            'filename': filename,
            'records': len(apps),
            'message': 'Export completed. Check your email for notification.',
        }
