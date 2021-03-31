from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from tdee_app.config import Config
from flask_graphql import GraphQLView

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

from tdee_app.models import schema

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
  #### create new database
  #  with app.app_context():
  #      db.create_all()

    from tdee_app.users.routes import users
    from tdee_app.data.routes import data
    from tdee_app.main.routes import main
    app.register_blueprint(users)
    app.register_blueprint(data)
    app.register_blueprint(main)
    
    return app