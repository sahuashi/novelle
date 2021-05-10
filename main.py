from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from views.routes import router
import os

# initialize flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY')
app.register_blueprint(router)

# setup database
db = SQLAlchemy(app)

# setup login manager
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

