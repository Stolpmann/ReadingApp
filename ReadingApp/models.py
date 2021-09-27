from ReadingApp import db, bcrypt, login_manager
from flask_login import UserMixin
import pandas as pd

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(30), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    booklist = db.relationship('Books', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.booklist}')"

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self,plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Books(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(150), unique=False, nullable=False)
    subject = db.Column(db.String(100), unique=False, nullable=False)
    hours = db.Column(db.Integer)
    input_user = db.Column(db.Integer(), db.ForeignKey('user.id'))
    date = db.Column(db.String(), unique=False, nullable=False)

    def __repr__(self):
        return f'{self.title}, {self.subject}, {self.hours}, {self.input_user}'

    def add_book(self, user):
        self.input_user = user.id
        db.session.commit()

