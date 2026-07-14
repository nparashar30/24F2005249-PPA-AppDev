from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.models import User, Company, Student, JobPosition, Application, Placement
from utils.auth_helpers import role_required
from utils.cache import cache_get, cache_set, cache_delete_pattern

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required('admin')
def dashboard():
    cache_key = 'admin:dashboard'
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)

    stats = {
        'total_students': Student.query.count(),
        'total_companies': Company.query.filter_by(approval_status='approved').count(),
        'pending_companies': Company.query.filter_by(approval_status='pending').count(),
        'total_drives': JobPosition.query.count(),
        'approved_drives': JobPosition.query.filter(JobPosition.status.in_(['approved', 'active'])).count(),
        'pending_drives': JobPosition.query.filter_by(status='pending').count(),
        'total_applications': Application.query.count(),
        'total_placements': Placement.query.count(),
    }
    cache_set(cache_key, stats, ttl=120)
    return jsonify(stats)


@admin_bp.route('/companies', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_companies():
    status = request.args.get('status')
    search = request.args.get('search', '').strip()
    query = Company.query
    if status:
        query = query.filter_by(approval_status=status)
    if search:
        query = query.filter(
            db.or_(
                Company.company_name.ilike(f'%{search}%'),
                Company.industry.ilike(f'%{search}%'),
            )
        )
    companies = query.order_by(Company.created_at.desc()).all()
    return jsonify([c.to_dict() for c in companies])


@admin_bp.route('/companies/<int:company_id>/approve', methods=['PUT'])
@jwt_required()
@role_required('admin')
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    action = request.get_json().get('action', 'approve')
    company.approval_status = 'approved' if action == 'approve' else 'rejected'
    db.session.commit()
    cache_delete_pattern('admin:*')
    cache_delete_pattern('jobs:*')
    return jsonify({'message': f'Company {action}d', 'company': company.to_dict()})


@admin_bp.route('/companies/<int:company_id>/deactivate', methods=['PUT'])
@jwt_required()
@role_required('admin')
def deactivate_company(company_id):
    company = Company.query.get_or_404(company_id)
    user = User.query.get(company.user_id)
    data = request.get_json() or {}
    blacklist = data.get('blacklist', False)
    user.is_active = False
    if blacklist:
        user.is_blacklisted = True
    db.session.commit()
    cache_delete_pattern('admin:*')
    return jsonify({'message': 'Company deactivated', 'company': company.to_dict()})


@admin_bp.route('/companies/<int:company_id>/reactivate', methods=['PUT'])
@jwt_required()
@role_required('admin')
def reactivate_company(company_id):
    company = Company.query.get_or_404(company_id)
    user = User.query.get(company.user_id)
    user.is_active = True
    user.is_blacklisted = False
    db.session.commit()
    cache_delete_pattern('admin:*')
    return jsonify({'message': 'Company reactivated', 'company': company.to_dict()})


@admin_bp.route('/students', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_students():
    search = request.args.get('search', '').strip()
    query = Student.query.join(User)
    if search:
        query = query.filter(
            db.or_(
                Student.full_name.ilike(f'%{search}%'),
                Student.student_id.ilike(f'%{search}%'),
                Student.phone.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
            )
        )
    students = query.order_by(Student.created_at.desc()).all()
    return jsonify([s.to_dict() for s in students])


@admin_bp.route('/students/<int:student_id>/deactivate', methods=['PUT'])
@jwt_required()
@role_required('admin')
def deactivate_student(student_id):
    student = Student.query.get_or_404(student_id)
    user = User.query.get(student.user_id)
    data = request.get_json() or {}
    blacklist = data.get('blacklist', False)
    user.is_active = False
    if blacklist:
        user.is_blacklisted = True
    db.session.commit()
    cache_delete_pattern('admin:*')
    return jsonify({'message': 'Student deactivated', 'student': student.to_dict()})


@admin_bp.route('/students/<int:student_id>/reactivate', methods=['PUT'])
@jwt_required()
@role_required('admin')
def reactivate_student(student_id):
    student = Student.query.get_or_404(student_id)
    user = User.query.get(student.user_id)
    user.is_active = True
    user.is_blacklisted = False
    db.session.commit()
    cache_delete_pattern('admin:*')
    return jsonify({'message': 'Student reactivated', 'student': student.to_dict()})


@admin_bp.route('/drives', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_drives():
    status = request.args.get('status')
    query = JobPosition.query
    if status:
        query = query.filter_by(status=status)
    drives = query.order_by(JobPosition.created_at.desc()).all()
    return jsonify([d.to_dict() for d in drives])


@admin_bp.route('/drives/<int:drive_id>/approve', methods=['PUT'])
@jwt_required()
@role_required('admin')
def approve_drive(drive_id):
    drive = JobPosition.query.get_or_404(drive_id)
    action = request.get_json().get('action', 'approve')
    if action == 'approve':
        drive.status = 'approved'
    else:
        drive.status = 'rejected'
    db.session.commit()
    cache_delete_pattern('admin:*')
    cache_delete_pattern('jobs:*')
    return jsonify({'message': f'Drive {action}d', 'drive': drive.to_dict()})


@admin_bp.route('/applications', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_applications():
    apps = Application.query.order_by(Application.application_date.desc()).all()
    return jsonify([a.to_dict() for a in apps])


@admin_bp.route('/reports/stats', methods=['GET'])
@jwt_required()
@role_required('admin')
def placement_stats():
    cache_key = 'admin:placement_stats'
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)

    from sqlalchemy import func
    by_status = db.session.query(
        Application.status, func.count(Application.id)
    ).group_by(Application.status).all()

    by_company = db.session.query(
        Company.company_name, func.count(Placement.id)
    ).join(Placement).group_by(Company.company_name).all()

    stats = {
        'applications_by_status': {s: c for s, c in by_status},
        'placements_by_company': {n: c for n, c in by_company},
    }
    cache_set(cache_key, stats, ttl=300)
    return jsonify(stats)
