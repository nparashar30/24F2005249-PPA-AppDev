from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.models import User, Company, Student, JobPosition, Application, Placement
