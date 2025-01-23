from __init__ import db, app
from model.librarydb import Book
from model.user import User  # Assuming the User model is defined in model/user.py
from sqlalchemy.exc import IntegrityError

# Define the Wishlist model
class Wishlist(db.Model):
    __tablename__ = 'wishlist'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to users table

    book = db.relationship('Book', backref='wishlist', lazy=True)
    user = db.relationship('User', backref='wishlist', lazy=True)  # Relationship to User model

    def __repr__(self):
        return f"<Wishlist(id={self.id}, book_id={self.book_id}, user_id={self.user_id})>"

    def read(self):
        """Return a dictionary representation of the Wishlist item."""
        return {
            "id": self.id,
            "book_id": self.book_id,
            "user_id": self.user_id,
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

# Function to delete a book from a user's wishlist
def delete_from_wishlist(user_id, book_id):
    """
    Delete a book from a user's wishlist by its book_id.

    Args:
        user_id (int): The ID of the user.
        book_id (int): The ID of the book to be removed from the wishlist.

    Returns:
        str: A success or error message.
    """
    with app.app_context():
        try:
            item = Wishlist.query.filter_by(user_id=user_id, book_id=book_id).first()
            if item:
                db.session.delete(item)
                db.session.commit()
                return f"Book with id {book_id} removed from user {user_id}'s wishlist."
            else:
                return f"Book with id {book_id} not found in user {user_id}'s wishlist."
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
            Wishlist(book_id=1, user_id=1),
            Wishlist(book_id=2, user_id=2),
            Wishlist(book_id=3, user_id=1),
        ]
        
        for item in wishlist_items:
            try:
                db.session.add(item)
                db.session.commit()
                print(f"Wishlist item created: {repr(item)}")
            except IntegrityError:
                db.session.rollback()
                print(f"Duplicate or error: {repr(item)}")

# Function to fetch a user's wishlist
def get_wishlist_by_user(user_id):
    """
    Get all wishlist items for a specific user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        list: A list of wishlist items for the user.
    """
    with app.app_context():
        return Wishlist.query.filter_by(user_id=user_id).all()

# Function to add a book to a user's wishlist
def add_to_wishlist(user_id, book_id):
    """
    Add a book to a user's wishlist.

    Args:
        user_id (int): The ID of the user.
        book_id (int): The ID of the book to add.

    Returns:
        str: A success or error message.
    """
    with app.app_context():
        try:
            item = Wishlist(book_id=book_id, user_id=user_id)
            db.session.add(item)
            db.session.commit()
            return f"Book with id {book_id} added to user {user_id}'s wishlist."
        except IntegrityError:
            db.session.rollback()
            return f"Book with id {book_id} already exists in user {user_id}'s wishlist."
        except Exception as e:
            db.session.rollback()
            return f"An error occurred: {str(e)}"
