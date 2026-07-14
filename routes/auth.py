from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models import db
from models.models import User, Company, Student
from utils.auth_helpers import validate_registration

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    if not user.is_active or user.is_blacklisted:
        return jsonify({'error': 'Account is deactivated or blacklisted'}), 403

    if user.role == 'company' and user.company and user.company.approval_status != 'approved':
        return jsonify({'error': 'Company account pending admin approval'}), 403

    token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'email': user.email}
    )

    profile = None
    if user.role == 'company' and user.company:
        profile = user.company.to_dict()
    elif user.role == 'student' and user.student:
        profile = user.student.to_dict()

    return jsonify({
        'token': token,
        'user': user.to_dict(),
        'profile': profile,
    })


@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.get_json() or {}
    errors = validate_registration(data, 'student')
    if errors:
        return jsonify({'errors': errors}), 400

    email = data['email'].strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    student_id = data['student_id'].strip()
    if Student.query.filter_by(student_id=student_id).first():
        return jsonify({'error': 'Student ID already exists'}), 409

    user = User(email=email, role='student')
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()

    student = Student(
        user_id=user.id,
        student_id=student_id,
        full_name=data['full_name'].strip(),
        branch=data.get('branch', ''),
        year=data.get('year'),
        cgpa=data.get('cgpa'),
        phone=data.get('phone', ''),
        skills=data.get('skills', ''),
        education=data.get('education', ''),
    )
    db.session.add(student)
    db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'email': user.email}
    )
    return jsonify({
        'message': 'Registration successful',
        'token': token,
        'user': user.to_dict(),
        'profile': student.to_dict(),
    }), 201


@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    data = request.get_json() or {}
    errors = validate_registration(data, 'company')
    if errors:
        return jsonify({'errors': errors}), 400

    email = data['email'].strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(email=email, role='company')
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()

    company = Company(
        user_id=user.id,
        company_name=data['company_name'].strip(),
        industry=data.get('industry', ''),
        location=data.get('location', ''),
        website=data.get('website', ''),
        hr_contact=data.get('hr_contact', ''),
        hr_email=data.get('hr_email', email),
        description=data.get('description', ''),
        approval_status='pending',
    )
    db.session.add(company)
    db.session.commit()

    return jsonify({
        'message': 'Company registered. Awaiting admin approval.',
        'user': user.to_dict(),
        'profile': company.to_dict(),
    }), 201


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    profile = None
    if user.role == 'company' and user.company:
        profile = user.company.to_dict()
    elif user.role == 'student' and user.student:
        profile = user.student.to_dict()

    return jsonify({'user': user.to_dict(), 'profile': profile})


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Logged out successfully'})
