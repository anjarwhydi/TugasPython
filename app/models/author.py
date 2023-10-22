from ..utils import db

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    books = db.relationship('Book', backref='author')

    def __init__(self, name):
        self.name = name
