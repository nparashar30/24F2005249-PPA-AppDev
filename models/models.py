from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from models import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, company, student
    is_active = db.Column(db.Boolean, default=True)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref='user', uselist=False, cascade='all, delete-orphan')
    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'is_blacklisted': self.is_blacklisted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    company_name = db.Column(db.String(200), nullable=False, index=True)
    industry = db.Column(db.String(100))
    location = db.Column(db.String(200))
    website = db.Column(db.String(300))
    hr_contact = db.Column(db.String(100))
    hr_email = db.Column(db.String(120))
    description = db.Column(db.Text)
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    job_positions = db.relationship('JobPosition', backref='company', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'industry': self.industry,
            'location': self.location,
            'website': self.website,
            'hr_contact': self.hr_contact,
            'hr_email': self.hr_email,
            'description': self.description,
            'approval_status': self.approval_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(150), nullable=False, index=True)
    branch = db.Column(db.String(100))
    year = db.Column(db.Integer)
    cgpa = db.Column(db.Float)
    phone = db.Column(db.String(20))
    skills = db.Column(db.Text)
    education = db.Column(db.Text)
    experience = db.Column(db.Text)
    resume_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    applications = db.relationship('Application', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    placements = db.relationship('Placement', backref='student', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'student_id': self.student_id,
            'full_name': self.full_name,
            'branch': self.branch,
            'year': self.year,
            'cgpa': self.cgpa,
            'phone': self.phone,
            'skills': self.skills,
            'education': self.education,
            'experience': self.experience,
            'resume_path': self.resume_path,
            'email': self.user.email if self.user else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class JobPosition(db.Model):
    __tablename__ = 'job_positions'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    skills_required = db.Column(db.Text)
    experience_required = db.Column(db.String(100))
    salary = db.Column(db.String(100))
    benefits = db.Column(db.Text)
    eligibility_branch = db.Column(db.String(200))
    eligibility_cgpa = db.Column(db.Float)
    eligibility_year = db.Column(db.Integer)
    application_deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, approved, active, closed, rejected
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    applications = db.relationship('Application', backref='job_position', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        company_name = self.company.company_name if self.company else None
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': company_name,
            'title': self.title,
            'description': self.description,
            'skills_required': self.skills_required,
            'experience_required': self.experience_required,
            'salary': self.salary,
            'benefits': self.benefits,
            'eligibility_branch': self.eligibility_branch,
            'eligibility_cgpa': self.eligibility_cgpa,
            'eligibility_year': self.eligibility_year,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_positions.id'), nullable=False, index=True)
    application_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(30), default='applied')
    # applied, shortlisted, interview, offer, selected, rejected, placed
    feedback = db.Column(db.Text)
    interview_date = db.Column(db.DateTime)
    interview_location = db.Column(db.String(300))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('student_id', 'job_id', name='unique_student_job_application'),
    )

    def to_dict(self):
        job = self.job_position
        return {
            'id': self.id,
            'student_id': self.student_id,
            'job_id': self.job_id,
            'job_title': job.title if job else None,
            'company_name': job.company.company_name if job and job.company else None,
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'status': self.status,
            'feedback': self.feedback,
            'interview_date': self.interview_date.isoformat() if self.interview_date else None,
            'interview_location': self.interview_location,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'student': self.student.to_dict() if self.student else None,
        }


class Placement(db.Model):
    __tablename__ = 'placements'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_positions.id'), nullable=True)
    position = db.Column(db.String(200))
    salary = db.Column(db.String(100))
    joining_date = db.Column(db.Date)
    offer_letter_path = db.Column(db.String(500))
    placed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref='placements')
    job_position = db.relationship('JobPosition', backref='placements')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'company_id': self.company_id,
            'company_name': self.company.company_name if self.company else None,
            'job_id': self.job_id,
            'position': self.position,
            'salary': self.salary,
            'joining_date': self.joining_date.isoformat() if self.joining_date else None,
            'offer_letter_path': self.offer_letter_path,
            'placed_at': self.placed_at.isoformat() if self.placed_at else None,
        }
