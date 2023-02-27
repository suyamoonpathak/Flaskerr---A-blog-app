from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "database.db"


app = Flask(__name__)
app.config['SECRET_KEY'] = "secret"
# UPLOAD_FOLDER = '/Users/suyamoonpathak/Desktop/IITM BlogLiteApp/siteFiles/static/images/uploads'
UPLOAD_FOLDER = path.join(path.dirname(
    path.realpath(__file__)), 'static/images/uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

db.init_app(app)

from .views import views
from .authentication import authentication

app.register_blueprint(views, url_prefix="/")
app.register_blueprint(authentication, url_prefix="/")

from .models import User, Post, Comment, Like

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = "authentication.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
