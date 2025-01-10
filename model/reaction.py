from flask_restful import Api, Resource
from sqlalchemy import Text, JSON
from __init__ import app, db
from sqlalchemy import Column, Integer, String, Text
from sqlite3 import IntegrityError

# Book model definition
class Reaction(db.Model):
    __tablename__ = 'reactions'
    id = db.Column(String, primary_key=True)
    # title = db.Column(String, nullable=False)
    # author = db.Column(String, nullable=False)
    # genre = db.Column(String)
    # description = db.Column(Text)
    # cover_image_url = db.Column(String)

# Book data to insert
def initReactions(): 
    reactions_data = [
        "👍", "❤️", "😂", "🎉", "😢", "😡"
    ]  
  
    # Insert the books data into the table
    for reaction in reactions_data:
        new_reaction = Reaction(
            id=reaction[0],
        )
        db.session.add(new_reaction)
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        print("IntegrityError: Could be a duplicate entry or violation of database constraints.")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")

# Create the tables before inserting data
with app.app_context():
    db.create_all()
    initReactions()