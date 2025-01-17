from flask_restful import Api, Resource
from sqlalchemy import Text, JSON
from __init__ import app, db
from sqlalchemy import Column, Integer, String, Text
from sqlite3 import IntegrityError
from model.librarydb import Book
from model.user import User

class Comments(db.Model):
    __tablename__ = 'comments'
    id = db.Column(Integer, primary_key=True)
    book_id = db.Column(Integer, db.ForeignKey(Book.id), nullable=False)
    username = db.Column(String, db.ForeignKey(User._name), nullable=False)
    comment_text = db.Column(Text, nullable=False)

    # CRUD methods
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
            'book_id': self.book_id,
            'username': self.username,
            'comment_text': self.comment_text
        }

    def update(self, inputs):
        if not isinstance(inputs, dict):
            return self

        book_id = inputs.get("book_id", None)
        username = inputs.get("username", "")
        comment_text = inputs.get("comment_text", "")

        if book_id is not None:
            self.book_id = book_id
        if username:
            self.username = username
        if comment_text:
            self.comment_text = comment_text

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return self

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def restore(data):
        """
        Restores a list of comments from the provided data. If a comment with the same
        book_id and username already exists, it updates it; otherwise, it creates a new one.

        Args:
            data (list): A list of dictionaries containing comment data.

        Returns:
            dict: A dictionary of restored comments (comment id as keys).
        """
        restored_comments = {}

        for comment_data in data:
            # Remove 'id' from the data if it exists (because id will be auto-generated)
            _ = comment_data.pop('id', None)

            # Check if the comment already exists based on book_id and username
            existing_comment = Comments.query.filter_by(
                book_id=comment_data.get("book_id"),
                username=comment_data.get("username")
            ).first()

            if existing_comment:
                # Update the existing comment with new data
                existing_comment.update(comment_data)
                restored_comments[existing_comment.id] = existing_comment
            else:
                # Create a new comment
                new_comment = Comments(**comment_data)
                new_comment.create()
                restored_comments[new_comment.id] = new_comment

        return restored_comments


def initComments():
    comments = [
        {
            "comment_id": 1,
            "book_id": 1,  # Reference to the book "Thomas Edison"
            "comment_text": "I loved this book!",
            "username": "Thomas Edison",  # Ensure this matches an existing user in your database
        },
        {
            "comment_id": 2,
            "book_id": 1,
            "comment_text": "This was an amazing read! Highly recommend.",
            "username": "Thomas Edison",  # Ensure this matches an existing user
        },
        {
            "comment_id": 3,
            "book_id": 2,  # Reference to a different book
            "comment_text": "Really insightful. The chapters on his inventions were fantastic.",
            "username": "Thomas Edison",  # Ensure this matches an existing user
        }
    ]
    
    for comment in comments:
        # Check for duplicate entries to avoid IntegrityError
        existing_comment = Comments.query.filter_by(id=comment["comment_id"]).first()
        if not existing_comment:
            new_comment = Comments(
                id=comment["comment_id"],
                book_id=comment["book_id"],
                comment_text=comment["comment_text"],
                username=comment["username"]
            )
            db.session.add(new_comment)

    try:
        db.session.commit()  # Commit the changes
    except IntegrityError:
        db.session.rollback()  # Rollback if there is an integrity error
        print("IntegrityError: Could be a duplicate entry or violation of database constraints.")
    except Exception as e:
        db.session.rollback()  # Rollback for other errors
        print(f"Error: {e}")


# Create the tables and initialize data
with app.app_context():
    db.create_all()  # Create tables
    initComments()  # Initialize the comments data
