from . import db
import uuid

class User(db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    posts = db.relationship('Survey', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.email)
    

class Survey(db.Model):
    __tablename__="survey"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(10))
    answers = db.Column(db.String(200))
    # submitted = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_done = db.Column(db.Boolean, unique=False, default=False)

    def __repr__(self):
        return '<Survey {}>'.format(self.token)
    