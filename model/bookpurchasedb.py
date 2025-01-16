from flask_restful import Api, Resource
from sqlalchemy import Text, JSON
from __init__ import app, db
from sqlalchemy import Column, Integer, String, Text
from sqlite3 import IntegrityError

# Database model for the cart
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'quantity': self.quantity
        }

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
@app.before_first_request
def create_tables():
    db.create_all()
    CartItem()  # Initialize the items in the cart





