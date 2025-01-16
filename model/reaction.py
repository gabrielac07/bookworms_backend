from flask_restful import Api, Resource
from sqlalchemy import Text, JSON
from __init__ import app, db
from sqlalchemy import Column, Integer, String, Text
from sqlite3 import IntegrityError

# Reaction model definition
class Reaction(db.Model):
    __tablename__ = 'reactions'
    id = db.Column(Integer, primary_key=True)
    _reaction_type = db.Column(String, nullable=False)
    _user_id = db.Column(String, db.ForeignKey('users.id'), nullable=False)
    _user_id = db.Column(String, db.ForeignKey('users.id'), nullable=False)
#    genre = db.Column(String)
#    description = db.Column(Text)
#    cover_image_url = db.Column(String)


    def __init__(self, reaction_type, user_id, post_id):
        """
        Constructor to initialize a vote.

        Args:
            vote_type (str): Type of the vote, either "upvote" or "downvote".
            user_id (int): ID of the user who cast the vote.
            post_id (int): ID of the post that received the vote.
        """
        self._reaction_type = reaction_type
        self._user_id = user_id
        self._post_id = post_id



# reaction data to insert
def initReactions(): 
    reactions_data = [
        "👍", "❤️", "😂", "🎉", "😢", "😡"
    ]  
  
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()

        # Optionally, add some test data (replace with actual values as needed)
        reactions = [
            Reaction(vote_type='😢', user_id=1, post_id=1),
            Reaction(vote_type='❤️', user_id=2, post_id=1),
        ]
        
        for react in reactions:
            try:
                db.session.add(react)
                db.session.commit()
                print(f"Record created: {repr(react)}")
            except IntegrityError:
                db.session.rollback()
                print(f"Duplicate or error: {repr(react)}")