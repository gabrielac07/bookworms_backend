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
    id = Column(db.Integer, primary_key=True)
    title = Column(String, db.ForeignKey(Book.title), nullable=False)
    price = Column(db.Float, nullable=False)
    quantity = Column(db.Integer, nullable=False)
    username = Column(String, db.ForeignKey(User._name), nullable=False)

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def read(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'quantity': self.quantity,
            'username': self.username
        }

    @staticmethod
    def restore(cart_data):
        """Restores a list of cart items from given data."""
        for item in cart_data:
            existing_cart_item = CartItem.query.filter_by(title=item["title"], username=item["username"]).first()
            if not existing_cart_item:
                new_cart_item = CartItem(
                    title=item["title"],
                    price=item["price"],
                    quantity=item["quantity"],
                    username=item["username"]
                )
                db.session.add(new_cart_item)

        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            print(f"IntegrityError: {e}")
        except Exception as e:
            db.session.rollback()
            print(f"Unexpected error: {e}")

# Initialize cart items
def init_books_in_cart():
    books_in_cart = [
        {"id": 1, "title": "1984", "price": 15.00, "quantity": 2, "username": "Avika"},
        {"id": 2, "title": "The Hobbit", "price": 12.00, "quantity": 1, "username": "Soumini"},
        {"id": 3, "title": "The Outsiders", "price": 10.00, "quantity": 4, "username": "Aarush"},
        {"id": 4, "title": "A Game of Thrones", "price": 13.00, "quantity": 1, "username": "Aditi"},
        {"id": 5, "title": "The Nightingale", "price": 16.00, "quantity": 2, "username": "Thomas Edison"}
    ]

    CartItem.restore(books_in_cart)  # Use restore method to populate the database

# Initialize the database
with app.app_context():
    db.create_all()  # Create tables
    init_books_in_cart()
