from ..utils import db

class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    
    books = db.relationship('Book', secondary='borrowing')

    def __init__(self, name, phone):
        self.name = name
        self.phone = phone