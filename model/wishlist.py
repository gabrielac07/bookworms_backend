from __init__ import db
from model.librarydb import Book  # Ensure the Book model is correctly imported

# Define the Wishlist model
class Wishlist(db.Model):
    __tablename__ = 'wishlist'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)

    book = db.relationship('Book', backref='wishlist', lazy=True)

    def __repr__(self):
        return f"<Wishlist(id={self.id}, book_id={self.book_id})>"
