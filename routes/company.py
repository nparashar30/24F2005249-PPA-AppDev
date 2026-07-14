from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.models import User, Company, JobPosition, Application, Placement, Student
from utils.auth_helpers import role_required
from utils.cache import cache_delete_pattern

company_bp = Blueprint('company', __name__)


def _get_company():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or not user.company:
        return None
    return user.company


@company_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required('company')
def dashboard():
    company = _get_company()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404
    if company.approval_status != 'approved':
        return jsonify({'error': 'Company not approved yet'}), 403

    drives = company.job_positions.all()
    drive_stats = []
    for d in drives:
        drive_stats.append({
            **d.to_dict(),
            'applicant_count': d.applications.count(),
        })

    return jsonify({
        'company': company.to_dict(),
        'drives': drive_stats,
        'total_applications': sum(d.applications.count() for d in drives),
    })


@company_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
@role_required('company')
def profile():
    company = _get_company()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    if request.method == 'GET':
        return jsonify(company.to_dict())

    data = request.get_json() or {}
    for field in ['company_name', 'industry', 'location', 'website', 'hr_contact', 'hr_email', 'description']:
        if field in data:
            setattr(company, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Profile updated', 'company': company.to_dict()})


@company_bp.route('/drives', methods=['GET', 'POST'])
@jwt_required()
@role_required('company')
def drives():
    company = _get_company()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404
    if company.approval_status != 'approved':
        return jsonify({'error': 'Company must be approved to create drives'}), 403

    if request.method == 'GET':
        status = request.args.get('status')
        query = company.job_positions
        if status:
            query = query.filter_by(status=status)
        return jsonify([d.to_dict() for d in query.order_by(JobPosition.created_at.desc()).all()])

    data = request.get_json() or {}
    if not data.get('title'):
        return jsonify({'error': 'Job title is required'}), 400

    deadline = None
    if data.get('application_deadline'):
        deadline = datetime.fromisoformat(data['application_deadline'].replace('Z', '+00:00'))

    drive = JobPosition(
        company_id=company.id,
        title=data['title'],
        description=data.get('description', ''),
        skills_required=data.get('skills_required', ''),
        experience_required=data.get('experience_required', ''),
        salary=data.get('salary', ''),
        benefits=data.get('benefits', ''),
        eligibility_branch=data.get('eligibility_branch', ''),
        eligibility_cgpa=data.get('eligibility_cgpa'),
        eligibility_year=data.get('eligibility_year'),
        application_deadline=deadline,
        status='pending',
    )
    db.session.add(drive)
    db.session.commit()
    cache_delete_pattern('jobs:*')
    cache_delete_pattern('admin:*')
    return jsonify({'message': 'Drive created, pending admin approval', 'drive': drive.to_dict()}), 201


@company_bp.route('/drives/<int:drive_id>/status', methods=['PUT'])
@jwt_required()
@role_required('company')
def update_drive_status(drive_id):
    company = _get_company()
    drive = JobPosition.query.filter_by(id=drive_id, company_id=company.id).first_or_404()
    data = request.get_json() or {}
    new_status = data.get('status')
    if new_status not in ('active', 'closed'):
        return jsonify({'error': 'Invalid status. Use active or closed'}), 400
    if drive.status not in ('approved', 'active', 'closed'):
        return jsonify({'error': 'Drive must be approved first'}), 400
    drive.status = new_status
    db.session.commit()
    cache_delete_pattern('jobs:*')
    return jsonify({'message': 'Drive status updated', 'drive': drive.to_dict()})


@company_bp.route('/drives/<int:drive_id>/applications', methods=['GET'])
@jwt_required()
@role_required('company')
def drive_applications(drive_id):
    company = _get_company()
    drive = JobPosition.query.filter_by(id=drive_id, company_id=company.id).first_or_404()
    apps = drive.applications.order_by(Application.application_date.desc()).all()
    return jsonify([a.to_dict() for a in apps])


@company_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
@jwt_required()
@role_required('company')
def update_application_status(app_id):
    company = _get_company()
    app = Application.query.get_or_404(app_id)
    if app.job_position.company_id != company.id:
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json() or {}
    status = data.get('status')
    valid = ('applied', 'shortlisted', 'interview', 'offer', 'selected', 'rejected', 'placed')
    if status not in valid:
        return jsonify({'error': f'Invalid status. Use one of: {valid}'}), 400

    app.status = status
    app.feedback = data.get('feedback', app.feedback)
    if data.get('interview_date'):
        app.interview_date = datetime.fromisoformat(data['interview_date'].replace('Z', '+00:00'))
    if data.get('interview_location'):
        app.interview_location = data['interview_location']
    app.updated_at = datetime.now(timezone.utc)

    if status in ('selected', 'placed'):
        existing = Placement.query.filter_by(
            student_id=app.student_id, job_id=app.job_id
        ).first()
        if not existing:
            placement = Placement(
                student_id=app.student_id,
                company_id=company.id,
                job_id=app.job_id,
                position=app.job_position.title,
                salary=app.job_position.salary,
            )
            db.session.add(placement)

    db.session.commit()
    cache_delete_pattern('admin:*')
    return jsonify({'message': 'Application updated', 'application': app.to_dict()})


@company_bp.route('/students/<int:student_id>', methods=['GET'])
@jwt_required()
@role_required('company')
def view_student(student_id):
    student = Student.query.get_or_404(student_id)
    return jsonify(student.to_dict())
