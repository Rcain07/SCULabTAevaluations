import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    if os.environ.get('DATABASE_URL'):
        'postgres+psycopg2://sculabtadatabase:coen174!@database.azure.com:5432/sculabta'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
