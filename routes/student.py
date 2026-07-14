import os
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import db
from models.models import User, Student, JobPosition, Application, Placement
from utils.auth_helpers import role_required, check_eligibility
from utils.cache import cache_get, cache_set, cache_delete_pattern

student_bp = Blueprint('student', __name__)


def _get_student():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or not user.student:
        return None
    return user.student


@student_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required('student')
def dashboard():
    student = _get_student()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    approved_drives = JobPosition.query.filter(
        JobPosition.status.in_(['approved', 'active'])
    ).order_by(JobPosition.application_deadline.asc()).limit(10).all()

    my_apps = student.applications.order_by(Application.application_date.desc()).limit(5).all()

    return jsonify({
        'student': student.to_dict(),
        'approved_drives': [d.to_dict() for d in approved_drives],
        'recent_applications': [a.to_dict() for a in my_apps],
        'placement_count': student.placements.count(),
    })


@student_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
@role_required('student')
def profile():
    student = _get_student()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    if request.method == 'GET':
        return jsonify(student.to_dict())

    data = request.get_json() or {}
    for field in ['full_name', 'branch', 'year', 'cgpa', 'phone', 'skills', 'education', 'experience']:
        if field in data:
            setattr(student, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Profile updated', 'student': student.to_dict()})


@student_bp.route('/profile/resume', methods=['POST'])
@jwt_required()
@role_required('student')
def upload_resume():
    student = _get_student()
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file provided'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    allowed = {'pdf', 'doc', 'docx'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed:
        return jsonify({'error': 'Only PDF, DOC, DOCX allowed'}), 400

    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    filename = secure_filename(f'resume_{student.student_id}_{file.filename}')
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    student.resume_path = filename
    db.session.commit()
    return jsonify({'message': 'Resume uploaded', 'resume_path': filename})


@student_bp.route('/drives', methods=['GET'])
@jwt_required()
@role_required('student')
def list_drives():
    search = request.args.get('search', '').strip()
    company = request.args.get('company', '').strip()
    cache_key = f'jobs:student:{search}:{company}'
    cached = cache_get(cache_key)
    if cached and not request.args.get('nocache'):
        return jsonify(cached)

    from models.models import Company
    query = JobPosition.query.filter(JobPosition.status.in_(['approved', 'active']))
    if search:
        query = query.filter(
            db.or_(
                JobPosition.title.ilike(f'%{search}%'),
                JobPosition.skills_required.ilike(f'%{search}%'),
            )
        )
    if company:
        query = query.join(Company).filter(Company.company_name.ilike(f'%{company}%'))

    drives = query.order_by(JobPosition.created_at.desc()).all()
    student = _get_student()
    result = []
    for d in drives:
        item = d.to_dict()
        eligible, reason = check_eligibility(student, d)
        item['eligible'] = eligible
        item['eligibility_reason'] = reason
        item['already_applied'] = Application.query.filter_by(
            student_id=student.id, job_id=d.id
        ).first() is not None
        result.append(item)

    cache_set(cache_key, result, ttl=180)
    return jsonify(result)


@student_bp.route('/drives/<int:drive_id>/apply', methods=['POST'])
@jwt_required()
@role_required('student')
def apply_drive(drive_id):
    student = _get_student()
    drive = JobPosition.query.get_or_404(drive_id)

    if drive.status not in ('approved', 'active'):
        return jsonify({'error': 'Drive is not open for applications'}), 400

    from datetime import datetime

    if drive.application_deadline and drive.application_deadline < datetime.now():
        return jsonify({'error': 'Application deadline has passed'}), 400

    existing = Application.query.filter_by(student_id=student.id, job_id=drive_id).first()
    if existing:
        return jsonify({'error': 'Already applied to this drive'}), 409

    eligible, reason = check_eligibility(student, drive)
    if not eligible:
        return jsonify({'error': reason}), 400

    app = Application(student_id=student.id, job_id=drive_id, status='applied')
    db.session.add(app)
    db.session.commit()
    cache_delete_pattern('jobs:*')
    cache_delete_pattern('admin:*')
    return jsonify({'message': 'Application submitted', 'application': app.to_dict()}), 201


@student_bp.route('/applications', methods=['GET'])
@jwt_required()
@role_required('student')
def my_applications():
    student = _get_student()
    apps = student.applications.order_by(Application.application_date.desc()).all()
    return jsonify([a.to_dict() for a in apps])


@student_bp.route('/placements', methods=['GET'])
@jwt_required()
@role_required('student')
def my_placements():
    student = _get_student()
    placements = student.placements.order_by(Placement.placed_at.desc()).all()
    return jsonify([p.to_dict() for p in placements])


@student_bp.route('/history', methods=['GET'])
@jwt_required()
@role_required('student')
def placement_history():
    student = _get_student()
    apps = student.applications.order_by(Application.application_date.desc()).all()
    placements = student.placements.order_by(Placement.placed_at.desc()).all()
    return jsonify({
        'applications': [a.to_dict() for a in apps],
        'placements': [p.to_dict() for p in placements],
    })


@student_bp.route('/export/csv', methods=['POST'])
@jwt_required()
@role_required('student')
def export_csv():
    student = _get_student()
    from tasks.export_tasks import export_student_applications
    task = export_student_applications.delay(student.id, student.user.email)
    return jsonify({
        'message': 'Export started. You will be notified when complete.',
        'task_id': task.id,
    }), 202


@student_bp.route('/export/status/<task_id>', methods=['GET'])
@jwt_required()
@role_required('student')
def export_status(task_id):
    from celery_worker import celery
    result = celery.AsyncResult(task_id)
    response = {'task_id': task_id, 'status': result.status}
    if result.ready():
        response['result'] = result.result
    return jsonify(response)


@student_bp.route('/export/download/<filename>', methods=['GET'])
@jwt_required()
@role_required('student')
def download_export(filename):
    filepath = os.path.join(current_app.config['EXPORT_FOLDER'], secure_filename(filename))
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    return send_file(filepath, as_attachment=True, download_name=filename)
