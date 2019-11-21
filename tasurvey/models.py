from . import db
import uuid
import os

class User(db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True)
    scuid  = db.Column(db.String(11),unique=True)
    surveys = db.relationship('Survey', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.email)
    

class Survey(db.Model):
    __tablename__="survey"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(10))
    answers = db.Column(db.String(1000))
    # submitted = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_done = db.Column(db.Boolean, unique=False, default=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    def __repr__(self):
        return '<Survey {}>'.format(self.token)
    
class Class(db.Model):
    __tablename__="class"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    name = db.Column(db.String(10))
    size = db.Column(db.Integer)
    instructorEmail = db.Column(db.String(120))
    surveys = db.relationship('Survey',backref='class',lazy='dynamic')
    def __repr__(self):
        return '<Class {}>'.format(self.number)

if (os.getenv("FLASK_ENV") == "development"):
    db.drop_all()
    db.create_all()

