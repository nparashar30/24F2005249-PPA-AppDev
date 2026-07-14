import os
import csv
from datetime import datetime, timezone, timedelta
from celery_worker import celery


def _get_app_context():
    from app import create_app
    return create_app()


@celery.task(name='tasks.scheduled_tasks.send_daily_deadline_reminders')
def send_daily_deadline_reminders():
    app = _get_app_context()
    with app.app_context():
        from models.models import JobPosition, Application, Student, User
        from utils.notifications import send_email, send_gchat_message

        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        today = datetime.now(timezone.utc)

        drives = JobPosition.query.filter(
            JobPosition.status.in_(['approved', 'active']),
            JobPosition.application_deadline >= today,
            JobPosition.application_deadline <= tomorrow,
        ).all()

        count = 0
        for drive in drives:
            students = Student.query.join(Application).filter(
                Application.job_id == drive.id,
                Application.status == 'applied',
            ).all()

            for student in students:
                if student.user and student.user.email:
                    subject = f'Reminder: Deadline for {drive.title}'
                    body = f'''
                    <p>Hi {student.full_name},</p>
                    <p>The application deadline for <strong>{drive.title}</strong>
                    at <strong>{drive.company.company_name}</strong> is
                    <strong>{drive.application_deadline.strftime("%d %b %Y")}</strong>.</p>
                    '''
                    send_email(student.user.email, subject, body)
                    count += 1

            msg = f'Deadline tomorrow: {drive.title} ({drive.company.company_name})'
            send_gchat_message(msg)

        return {'reminders_sent': count, 'drives_checked': len(drives)}


@celery.task(name='tasks.scheduled_tasks.send_interview_reminders')
def send_interview_reminders():
    app = _get_app_context()
    with app.app_context():
        from models.models import Application, Student
        from utils.notifications import send_email, send_gchat_message

        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        today = datetime.now(timezone.utc)

        apps = Application.query.filter(
            Application.status == 'interview',
            Application.interview_date >= today,
            Application.interview_date <= tomorrow,
        ).all()

        count = 0
        for app_record in apps:
            student = app_record.student
            if student and student.user:
                subject = f'Interview Reminder: {app_record.job_position.title}'
                body = f'''
                <p>Hi {student.full_name},</p>
                <p>You have an interview scheduled for <strong>{app_record.job_position.title}</strong>
                at <strong>{app_record.job_position.company.company_name}</strong>.</p>
                <p>Date: <strong>{app_record.interview_date.strftime("%d %b %Y %H:%M")}</strong></p>
                <p>Location: {app_record.interview_location or "TBD"}</p>
                '''
                send_email(student.user.email, subject, body)
                send_gchat_message(f'Interview tomorrow for {student.full_name}: {app_record.job_position.title}')
                count += 1

        return {'interview_reminders_sent': count}


@celery.task(name='tasks.scheduled_tasks.send_monthly_admin_report')
def send_monthly_admin_report():
    app = _get_app_context()
    with app.app_context():
        from models import db
        from models.models import JobPosition, Application, Placement, Student, Company
        from sqlalchemy import func
        from utils.notifications import send_email
        from config import Config

        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 1:
            prev_month_start = month_start.replace(year=now.year - 1, month=12)
        else:
            prev_month_start = month_start.replace(month=now.month - 1)

        drives_conducted = JobPosition.query.filter(
            JobPosition.created_at >= prev_month_start,
            JobPosition.created_at < month_start,
        ).count()

        applications_count = Application.query.filter(
            Application.application_date >= prev_month_start,
            Application.application_date < month_start,
        ).count()

        selected_count = Application.query.filter(
            Application.updated_at >= prev_month_start,
            Application.updated_at < month_start,
            Application.status.in_(['selected', 'placed']),
        ).count()

        placements_count = Placement.query.filter(
            Placement.placed_at >= prev_month_start,
            Placement.placed_at < month_start,
        ).count()

        month_name = prev_month_start.strftime('%B %Y')
        html = f'''
        <html><body style="font-family:Arial,sans-serif;padding:20px;">
        <h2>Monthly Placement Activity Report – {month_name}</h2>
        <table border="1" cellpadding="10" cellspacing="0" style="border-collapse:collapse;">
        <tr><td><strong>Drives Conducted</strong></td><td>{drives_conducted}</td></tr>
        <tr><td><strong>Students Applied</strong></td><td>{applications_count}</td></tr>
        <tr><td><strong>Students Selected</strong></td><td>{selected_count}</td></tr>
        <tr><td><strong>Placements Confirmed</strong></td><td>{placements_count}</td></tr>
        <tr><td><strong>Total Students</strong></td><td>{Student.query.count()}</td></tr>
        <tr><td><strong>Approved Companies</strong></td><td>{Company.query.filter_by(approval_status="approved").count()}</td></tr>
        </table>
        <p><em>Generated on {now.strftime("%d %b %Y")}</em></p>
        </body></html>
        '''

        send_email(
            Config.ADMIN_REPORT_EMAIL,
            f'Placement Report – {month_name}',
            html,
        )
        return {
            'month': month_name,
            'drives_conducted': drives_conducted,
            'applications': applications_count,
            'selected': selected_count,
            'placements': placements_count,
        }
