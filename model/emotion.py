## model, backend
from flask_restful import Api, Resource
from sqlalchemy import Text, JSON
from __init__ import app, db
from sqlalchemy import Column, Integer, String, Text
from model.librarydb import Book
from sqlite3 import IntegrityError

# Reaction model definition
class Emotion(db.Model):
    __tablename__ = 'emotion'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False) #person
    title_id = db.Column(db.String, db.ForeignKey('books.title'), nullable=False) #book title/series
    author_id = db.Column(db.String, db.ForeignKey('books.author'), nullable=False) #author
    reaction_type = db.Column(db.String, nullable=False) #reaction

    def __init__(self, reaction_type, user_id, title_id, author_id):
        self.reaction_type = reaction_type
        self.user_id = user_id
        self.title_id = title_id
        self.author_id = author_id

    def add_reaction(reaction_type, user_id, title_id, author_id):
        new_reaction = Emotion (
            reaction_type=reaction_type,
            user_id=user_id,
            title_id=title_id,
            author_id=author_id
        )

        try:
            db.session.add(new_reaction)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def __repr__(self):
        return f"<Reaction {self.reaction_type}>"
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        """
        The delete method removes the object from the database and commits the transaction.
        
        Uses:
            The db ORM methods to delete and commit the transaction.
        
        Raises:
            Exception: An error occurred when deleting the object from the database.
        """    
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        
    def read(self):
        """
        Retrieve the vote data as a dictionary.

        Returns:
            dict: Dictionary with vote information.
        """
        return {
            "reaction_type": self.reaction_type,
            "user_id": self.user_id,
            "title_id": self.title_id,
            "author_id": self.author_id
        }
    
    @staticmethod
    def restore(data):
        """
        Restores a list of suggested books from the provided data. If a book with the same
        title already exists, it updates it; otherwise, it creates a new one.

        Args:
            data (list): A list of dictionaries containing suggested book data.

        Returns:
            dict: A dictionary of restored suggested books (book id as keys).
        """
        restored_reactions = {}

        for reaction_data in data:
            # Remove 'id' from the data if it exists (because id will be auto-generated)
            _ = reaction_data.pop('id', None)

            # Check if the reaction already exists for the same user and book
            existing_reaction = Emotion.query.filter_by(
                user_id=reaction_data.get("user_id"),
                title_id=reaction_data.get("title_id")
            ).first()

            if existing_reaction:
                # Update the existing reaction with new data
                existing_reaction.reaction_type = reaction_data.get('reaction_type', existing_reaction.reaction_type)
                existing_reaction.author_id = reaction_data.get('author_id', existing_reaction.author_id)

                db.session.commit()
                restored_reactions[existing_reaction.id] = existing_reaction
            else:
                # Create a new reaction
                new_reaction = Emotion(
                    reaction_type=reaction_data["reaction_type"],
                    user_id=reaction_data["user_id"],
                    title_id=reaction_data["title_id"],
                    author_id=reaction_data["author_id"]
                )
                new_reaction.create()
                restored_reactions[new_reaction.id] = new_reaction

        return restored_reactions


# reaction data to insert
def initEmotion(): 
    # reactions_data = [
    #     "👍", "❤️", "😂", "🎉", "😢", "😡"
    # ]  

    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        # Optionally, add some test data (replace with actual values as needed)

    # Optionally, add some test data (replace with actual values as needed)
    emotions = [
        Emotion(user_id=1, reaction_type='😢', title_id="Catcher in the Rye", author_id="J.D."),
        Emotion(user_id=1, reaction_type='❤️', title_id="Hunger Games", author_id="Suzanne Collins")
    ]
        
    for emoji in emotions:
        try:
            db.session.add(emoji)
            db.session.commit()
            print(f"Record created: {repr(emoji)}")
        except IntegrityError:
            db.session.rollback()
            print(f"Duplicate or error: {repr(emoji)}")


# # Create the tables and initialize data
# with app.app_context():
#     db.create_all()  # Create tables
#     initReactions()  # Initialize the comments data