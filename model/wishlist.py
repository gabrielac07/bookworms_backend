from __init__ import db, app
from model.librarydb import Book
from model.user import User
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the Wishlist model
class Wishlist(db.Model):
    __tablename__ = 'wishlist'

    id = db.Column(db.Integer, primary_key=True)
    user_uid = db.Column(db.String, db.ForeignKey('users._uid'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="for later")
    date_added = db.Column(db.Date, default=lambda: datetime.utcnow().date())
    availability = db.Column(db.String(20), nullable=False, default=lambda: random.choice(["available", "out of stock"]))

    user = db.relationship('User', backref='wishlist', lazy=True)
    book = db.relationship('Book', backref='wishlist', lazy=True)

    def __repr__(self):
        return f"<Wishlist(id={self.id}, user_uid={self.user_uid}, book_id={self.book_id}, status={self.status}, date_added={self.date_added}, availability={self.availability})>"

    def read(self):
        """Return a dictionary representation of the Wishlist item."""
        return {
            "id": self.id,
            "user_uid": self.user_uid,
            "book_id": self.book_id,
            "status": self.status,
            "date_added": self.date_added.strftime('%Y-%m-%d'),  # Format date to exclude time
            "availability": self.availability,
        }
        
    @classmethod
    def restore(cls, data):
        """
        Restore data to the Wishlist table.

        Args:
            data (list): A list of dictionaries where each dictionary represents a Wishlist item.
        
        Returns:
            list: The list of added Wishlist objects.
        """
        added_items = []
        with app.app_context():
            for record in data:
                try:
                    # Convert date_added from string to date object
                    if 'date_added' in record and isinstance(record['date_added'], str):
                        record['date_added'] = datetime.strptime(record['date_added'], '%Y-%m-%d').date()
                    
                    # Exclude 'id' to let the database auto-generate it
                    if 'id' in record:
                        del record['id']
                    
                    wishlist_item = cls(**record)  # Unpack dictionary into model fields
                    db.session.add(wishlist_item)
                    added_items.append(wishlist_item)
                except Exception as e:
                    db.session.rollback()
                    print(f"Failed to restore Wishlist item: {record}. Error: {str(e)}")
            db.session.commit()
        return added_items

# Function to delete a book from the wishlist
def delete_from_wishlist(user_uid, book_id):
    """
    Delete a book from the wishlist by its user_uid and book_id.

    Args:
        user_uid (str): The UID of the user.
        book_id (int): The ID of the book to be removed from the wishlist.

    Returns:
        str: A success or error message.
    """
    with app.app_context():
        try:
            item = Wishlist.query.filter_by(user_uid=user_uid, book_id=book_id).first()
            if item:
                db.session.delete(item)
                db.session.commit()
                return f"Book with id {book_id} removed from the wishlist."
            else:
                return f"Book with id {book_id} not found in the wishlist."
        except Exception as e:
            db.session.rollback()
            return f"An error occurred: {str(e)}"

# Function to initialize the Wishlist table
def initWishlist():
    """
    Initialize the Wishlist table with any required starter data.
    """
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()

        # Add starter data for Wishlist (replace with actual values as needed)
        wishlist_items = [
            Wishlist(user_uid='toby', book_id=1),
            Wishlist(user_uid='toby', book_id=2),
            Wishlist(user_uid='hop', book_id=3),
        ]
        
        for item in wishlist_items:
            try:
                db.session.add(item)
                db.session.commit()
                print(f"Wishlist item created: {repr(item)}")
            except IntegrityError:
                db.session.rollback()
                print(f"Duplicate or error: {repr(item)}")

# Function to fetch the wishlist
def get_wishlist(user_uid):
    """
    Get all wishlist items for a specific user.

    Args:
        user_uid (str): The UID of the user.

    Returns:
        list: A list of wishlist items.
    """
    with app.app_context():
        return Wishlist.query.filter_by(user_uid=user_uid).all()

# Function to add a book to the wishlist
def add_to_wishlist(user_uid, book_id):
    """
    Add a book to the wishlist.

    Args:
        user_uid (str): The UID of the user.
        book_id (int): The ID of the book to add.

    Returns:
        str: A success or error message.
    """
    with app.app_context():
        try:
            item = Wishlist(user_uid=user_uid, book_id=book_id)
            db.session.add(item)
            db.session.commit()
            return f"Book with id {book_id} added to the wishlist."
        except IntegrityError:
            db.session.rollback()
            return f"Book with id {book_id} already exists in the wishlist."
        except Exception as e:
            db.session.rollback()
            return f"An error occurred: {str(e)}"

# Function to update a wishlist item
def update_wishlist_item(id, new_status):
    """
    Update a wishlist item's status by its ID.

    Args:
        id (int): The ID of the wishlist item to update.
        new_status (str): The new status to set.

    Returns:
        str: A success or error message.
    """
    logger.info(f"Attempting to update wishlist item with ID: {id} to status: {new_status}")
    with app.app_context():
        try:
            item = Wishlist.query.get(id)
            if item:
                if new_status not in ["for later", "in progress", "finished"]:
                    logger.warning(f"Invalid status: {new_status} for wishlist item with ID: {id}")
                    return "Invalid status"
                item.status = new_status
                db.session.commit()
                logger.info(f"Wishlist item with ID {id} updated to status {new_status}.")
                return f"Wishlist item with id {id} updated to status {new_status}."
            else:
                logger.warning(f"Wishlist item with ID {id} not found.")
                return f"Wishlist item with id {id} not found."
        except Exception as e:
            logger.error(f"An error occurred while updating wishlist item with ID {id}: {str(e)}")
            db.session.rollback()
            return f"An error occurred: {str(e)}"
