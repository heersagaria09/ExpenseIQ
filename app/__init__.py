import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, send_from_directory, session
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

from app.config.settings import Config

load_dotenv()

def create_app():
    """Application factory pattern for Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_ACCESS_TOKEN_EXPIRES
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

    jwt = JWTManager(app)
    CORS(app, supports_credentials=True)

    # Create upload directories
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'receipts'), exist_ok=True)
    os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'statements'), exist_ok=True)

    # Jinja2 globals & filters
    app.jinja_env.globals['now'] = datetime.utcnow
    app.jinja_env.globals['enumerate'] = enumerate
    app.jinja_env.globals['any'] = any
    app.jinja_env.globals['all'] = all
    app.jinja_env.globals['max'] = max
    app.jinja_env.globals['min'] = min
    app.jinja_env.globals['abs'] = abs
    app.jinja_env.globals['len'] = len
    app.jinja_env.globals['sum'] = sum
    app.jinja_env.globals['zip'] = zip
    app.jinja_env.globals['range'] = range
    app.jinja_env.globals['list'] = list
    app.jinja_env.globals['int'] = int
    app.jinja_env.globals['float'] = float
    app.jinja_env.globals['str'] = str
    app.jinja_env.globals['round'] = round

    # Make request available in templates
    @app.context_processor
    def inject_globals():
        return {
            'request': request,
            'current_year': datetime.utcnow().year,
        }

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.expense_routes import expense_bp
    from app.routes.income_routes import income_bp
    from app.routes.analytics_routes import analytics_bp
    from app.routes.budget_routes import budget_bp
    from app.routes.goal_routes import goal_bp
    from app.routes.subscription_routes import subscription_bp
    from app.routes.notification_routes import notification_bp
    from app.routes.ai_routes import ai_bp
    from app.routes.statement_routes import statement_bp
    from app.routes.settings_routes import settings_bp
    from app.routes.calendar_routes import calendar_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(goal_bp)
    app.register_blueprint(subscription_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(statement_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(calendar_bp)

    @app.route('/')
    def index():
        return render_template('landing.html')

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, 'static', 'images'),
            'favicon.svg',
            mimetype='image/svg+xml'
        )

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    return app
