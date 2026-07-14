from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') not in roles:
                return jsonify({'error': 'Access denied'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def check_eligibility(student, job):
    """Return (eligible: bool, reason: str)."""
    if job.eligibility_cgpa and student.cgpa:
        if student.cgpa < job.eligibility_cgpa:
            return False, f'Minimum CGPA required: {job.eligibility_cgpa}'
    if job.eligibility_year and student.year:
        if student.year != job.eligibility_year:
            return False, f'Only year {job.eligibility_year} students eligible'
    if job.eligibility_branch and student.branch:
        branches = [b.strip().lower() for b in job.eligibility_branch.split(',')]
        if student.branch.lower() not in branches:
            return False, f'Branch {student.branch} not eligible'
    return True, 'Eligible'


def validate_registration(data, role):
    errors = []
    if not data.get('email'):
        errors.append('Email is required')
    if not data.get('password') or len(data.get('password', '')) < 6:
        errors.append('Password must be at least 6 characters')
    if role == 'student':
        if not data.get('full_name'):
            errors.append('Full name is required')
        if not data.get('student_id'):
            errors.append('Student ID is required')
    if role == 'company':
        if not data.get('company_name'):
            errors.append('Company name is required')
    return errors
