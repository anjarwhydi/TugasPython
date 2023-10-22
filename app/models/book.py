from ..utils import db

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    borrowers = db.relationship('Borrower', secondary='borrowing')

    def __init__(self, title, author_id):
        self.title = title
        self.author_id = author_id
