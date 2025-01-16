from flask_restful import Api, Resource
from sqlalchemy import Text, JSON
from __init__ import app, db
from sqlalchemy import Column, Integer, String, Text
from sqlite3 import IntegrityError
from model.librarydb import Book 
from model.user import User

# Database model for the cart
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(String, db.ForeignKey(Book.title), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    username = db.Column(String, db.ForeignKey(User._name), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'quantity': self.quantity,
            'username': self.username
        }


def init_books_in_cart():
    books_in_cart = [
        {
            "item_id": 1,
            "title": "1984",  
            "price": "$15",
            "quantity": "2",  # Ensure this matches an existing user in your database
            "username": "Avika"
        },
        {
            "item_id": 2,
            "title": "Animal Farm",  
            "price": "$12",
            "quantity": "1",  # Ensure this matches an existing user in your database
            "username": "Soumini"
        },
        {
            "item_id": 3,
            "title": "Bread Givers",  
            "price": "$10",
            "quantity": "4",  # Ensure this matches an existing user in your database
            "username": "Aarush"
        }
    ]

    for book in books_in_cart:
        # Check for duplicate entries to avoid IntegrityError
        existing_book = Book.query.filter_by(id=book["comment_id"]).first()
        if not existing_book:
            new_book = init_books_in_cart(
                id=books_in_cart["item_id"],
                title=books_in_cart["title"],
                price=books_in_cart["price"],
                quantity=books_in_cart["quantity"],
                username=books_in_cart["username"]
            )
            db.session.add(new_book)
            
# Commit the transaction to the database

    try:
        db.session.commit()  # Commit the changes
    except IntegrityError:
        db.session.rollback()  # Rollback if there is an integrity error
        print("IntegrityError: Could be a duplicate entry or violation of database constraints.")
    except Exception as e:
        db.session.rollback()  # Rollback for other errors
        print(f"Error: {e}")

        
# Initialize the database
with app.app_context():
    db.create_all()  # Create tables
    init_books_in_cart()





