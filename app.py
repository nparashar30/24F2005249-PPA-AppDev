import os
from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.company import company_bp
from routes.student import student_bp


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)
    # Change Jinja2 delimiters to avoid conflict with Vue.js
    app.jinja_env.variable_start_string = '[['
    app.jinja_env.variable_end_string = ']]'

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)

    db.init_app(app)
    CORS(app, resources={r'/api/*': {'origins': '*'}})
    JWTManager(app)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'app': 'Placement Portal V2'}

    @app.route('/api/public/stats')
    def public_stats():
        from utils.cache import cache_get, cache_set
        from models.models import Placement, JobPosition, Student

        cache_key = 'public:stats'
        cached = cache_get(cache_key)
        if cached:
            return cached

        stats = {
            'total_placements': Placement.query.count(),
            'active_drives': JobPosition.query.filter(
                JobPosition.status.in_(['approved', 'active'])
            ).count(),
            'total_students': Student.query.count(),
        }
        cache_set(cache_key, stats, ttl=600)
        return stats

    return app


app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
