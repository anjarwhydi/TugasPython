from ..utils import db

class Borrowing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrower.id'))
