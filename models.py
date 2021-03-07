from flask_login import UserMixin
from main import db

List = db.Table(
    'List',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('book_id', db.String(50), db.ForeignKey('book.id'), primary_key=True))


class Book(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(100))
    thumbnail = db.Column(db.String(400))
    googlebooks = db.Column(db.String(400))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    list = db.relationship('Book', secondary=List)
