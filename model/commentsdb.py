from flask_restful import Api, Resource
from sqlalchemy import Integer, String, Text
from __init__ import app, db
from sqlalchemy import Column
from sqlite3 import IntegrityError
from model.librarydb import Book
from model.user import User
from api.jwt_authorize import token_required

class Comments(db.Model):
    __tablename__ = 'comments'
    id = db.Column(Integer, primary_key=True)
    book_id = db.Column(Integer, db.ForeignKey('books.id'), nullable=False)  # Reference to Book.id
    user_id = db.Column(Integer, db.ForeignKey('users.id'), nullable=False)  # Reference to User.id
    comment_text = db.Column(Text, nullable=False)

    # Establish relationships
    book = db.relationship('Book', backref='comments')  # Relationship with Book
    user = db.relationship('User', backref='comments')  # Relationship with User

    # CRUD methods
    def create(self):
        # Check if the comment already exists for this user and book
        existing_comment = Comments.query.filter_by(
            book_id=self.book_id,
            user_id=self.user_id,
            comment_text=self.comment_text
        ).first()

        if existing_comment:
            # If the comment already exists, return a message indicating no change
            return {"message": "Comment already exists for this book and user."}, 400

        try:
            db.session.add(self)
            db.session.commit()
            return {"message": "Comment added successfully."}, 201
        except Exception as e:
            db.session.rollback()
            raise e

    def read(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'user_id': self.user_id,
            'comment_text': self.comment_text
        }

    def update(self, inputs):
        if not isinstance(inputs, dict):
            return self

        book_id = inputs.get("book_id", None)
        user_id = inputs.get("user_id", None)
        comment_text = inputs.get("comment_text", "")

        if book_id:
            self.book_id = book_id
        if user_id:
            self.user_id = user_id
        if comment_text:
            self.comment_text = comment_text

        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            print(f"IntegrityError occurred: {e}")
            return None

        return self

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

# Update initComments to prevent duplication
def initComments():
    comments = [
        {
            "book_id": 1,  # Reference to the book with ID 1 (ensure the book exists)
            "comment_text": "I loved this book!",
            "user_id": 1,  # Reference to the user with ID 1 (ensure the user exists)
        },
        {
            "book_id": 2,
            "comment_text": "This was an amazing read! Highly recommend.",
            "user_id": 1,
        },
        {
            "book_id": 4,  # Reference to the book with ID 1
            "comment_text": "Really insightful. The chapters on his inventions were fantastic.",
            "user_id": 1,  # Reference to the user with ID 1
        }
    ]

    # Ensure we're inside a context to manipulate the DB session
    for comment in comments:
        # Check if the comment already exists before adding it to the session
        existing_comment = Comments.query.filter_by(
            book_id=comment["book_id"],
            user_id=comment["user_id"],
            comment_text=comment["comment_text"]
        ).first()

        if not existing_comment:
            new_comment = Comments(
                book_id=comment["book_id"],
                comment_text=comment["comment_text"],
                user_id=comment["user_id"]
            )
            db.session.add(new_comment)
        else:
            print(f"Skipping existing comment: {comment}")

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