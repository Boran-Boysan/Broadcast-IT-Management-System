from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from Project.config import Config

db = SQLAlchemy()
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    from Project.models import Employee
    return Employee.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    # Login manager ayarları
    login_manager.login_view = "main.login"
    login_manager.login_message = "Bu sayfaya erişmek için giriş yapmalısınız."
    login_manager.login_message_category = "info"
    login_manager.session_protection = "strong"  # Session güvenliği

    from Project.routes import main
    app.register_blueprint(main)

    return app