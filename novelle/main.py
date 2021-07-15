import os
from flask import Flask
from flask_login import LoginManager
from novelle.views.routes import router
from novelle.models import db, User

# initialize flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY')
app.register_blueprint(router)

# initialize database
db.init_app(app)
with app.app_context():
    db.create_all()

# setup login manager
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
