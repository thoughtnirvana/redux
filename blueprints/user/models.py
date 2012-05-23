# vim: set fileencoding=utf-8 :
"""
User model.
"""
from config import db, bcrypt

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pw_hash = db.Column(db.String(80))
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)

    def __init__(self, email, password):
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.pw_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.pw_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username
