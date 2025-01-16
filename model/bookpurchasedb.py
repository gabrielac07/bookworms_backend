from flask_restful import Api, Resource
from sqlalchemy import Text, JSON
from __init__ import app, db
from sqlalchemy import Column, Integer, String, Float
from sqlite3 import IntegrityError
from model.librarydb import Book 
from model.user import User

# Database model for the cart
class CartItem(db.Model):
    __tablename__ = 'cart_items'
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

# Initialize cart items
def init_books_in_cart():
    books_in_cart = [
        {
            "title": "1984",  
            "price": 15.00,  
            "quantity": 2,  
            "username": "Avika"
        },
        {
            "title": "Animal Farm",  
            "price": 12.00,
            "quantity": 1,
            "username": "Soumini"
        },
        {
            "title": "Bread Givers",  
            "price": 10.00,
            "quantity": 4,
            "username": "Aarush"
        }
    ]

    for book in books_in_cart:
        # Check for duplicate entries to avoid IntegrityError
        existing_cart_item = CartItem.query.filter_by(title=book["title"], username=book["username"]).first()
        if not existing_cart_item:
            new_cart_item = CartItem(
                title=book["title"],
                price=book["price"],
                quantity=book["quantity"],
                username=book["username"]
            )
            db.session.add(new_cart_item)

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
