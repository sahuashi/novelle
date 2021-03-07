from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from views.routes import router

# initialize flask
app = Flask(__name__)
app.secret_key = 'secret'
app.register_blueprint(router)

# database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# user management setup
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))


if __name__ == "__main__":
    app.run()
