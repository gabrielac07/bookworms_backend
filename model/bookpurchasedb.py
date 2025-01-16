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
            'title' : self.title,
            'price': self.price,
            'quantity': self.quantity,
            'username': self.username
        }
        
# Initialize cart items
def init_books_in_cart():
    books_in_cart = [
        {"id": 1, "title": "1984", "price": 15.00, "quantity": 2, "_name": "Avika"},
        {"id": 2, "title": "The Hobbit", "price": 12.00, "quantity": 1, "_name": "Soumini"},
        {"id": 3, "title": "The Outsiders", "price": 10.00, "quantity": 4, "_name": "Aarush"},
        {"id": 4, "title": "A Game of Thrones", "price": 13.00, "quantity": 1, "_name": "Aditi"}
    ]

    for book in books_in_cart:
        # Check for duplicate entries to avoid IntegrityError
        existing_cart_item = CartItem.query.filter_by(title=book["title"], username=book["_name"]).first()
        if not existing_cart_item:
            new_cart_item = CartItem(
                title=book["title"],
                price=book["price"],
                quantity=book["quantity"],
                username=book["_name"]
            )
            db.session.add(new_cart_item)  # Add valid CartItem instances

    try:
        db.session.commit()  # Commit changes to the database
    except IntegrityError as e:
        db.session.rollback()
        print(f"IntegrityError: {e}")
    except Exception as e:
        db.session.rollback()
        print(f"Unexpected error: {e}")

# Initialize the database
with app.app_context():
    db.create_all()  # Create tables
    init_books_in_cart()
