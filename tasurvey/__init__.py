
import os
from flask import Flask, flash, request, redirect, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)
