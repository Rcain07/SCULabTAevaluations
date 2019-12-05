'''
Description: Functional file that initializes our app
'''
import os
from flask import Flask, flash, request, redirect, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_login import LoginManager
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager()
login.init_app(app)
login.login_view = 'login'
from tasurvey import views



