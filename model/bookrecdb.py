from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.exc import IntegrityError
from __init__ import db, app
from model.librarydb import Book
#import random

class SaveBookRec(db.Model): # Class to save a book recommendation
    __tablename__ = 'savedbookrecs' # name of the table
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String, nullable=False)
    author = db.Column(String, nullable=False)
    genre = db.Column(String)
    description = db.Column(Text)
    cover_image_url = db.Column(String)

    def __init__(self, title, author, genre, description, cover_image_url):
        self.title = title
        self.author = author
        self.genre = genre
        self.description = description
        self.cover_image_url = cover_image_url

# Static data
def initSavedBookRecs(): # Function to initialize the saved book recommendations
    saved_bookrecs_data = [
        ("A Clash of Kings", "George R. R. Martin", "Fantasy", "A Clash of Kings by George R. R. Martin is the second installment in the A Song of Ice and Fire series. The novel follows the chaos and power struggles that erupt across the Seven Kingdoms as multiple factions claim the Iron Throne following the death of King Robert Baratheon. Amid the political intrigue and battles, dark supernatural forces begin to rise, threatening the realm from the shadows.", "https://m.media-amazon.com/images/I/81ES5DAxprL.jpg"),
        ("A Storm of Swords", "George R. R. Martin", "Fantasy", "A Storm of Swords by George R. R. Martin is the third book in the A Song of Ice and Fire series. The novel continues the epic tale of political intrigue, betrayal, and warfare in the Seven Kingdoms. As the War of the Five Kings rages on, alliances are forged and broken, and the fate of Westeros hangs in the balance.", "https://m.media-amazon.com/images/I/819o5XLwuFL.jpg"),
        #("A Feast for Crows", "George R. R. Martin", "Fantasy", "A Feast for Crows by George R. R. Martin is the fourth book in the A Song of Ice and Fire series. The novel follows the aftermath of the War of the Five Kings as the Seven Kingdoms struggle to recover from the devastation and chaos. As new threats emerge and old rivalries resurface, the realm faces an uncertain future.", "https://m.media-amazon.com/images/I/91Tpg6BX00L._UF1000,1000_QL80_.jpg")
    ]

# insert the books data into the table
    '''
    for book in saved_bookrecs_data:
        if not Book.query.filter_by(title=book[0]).first():  # Check if book already exists
            save_newbookrec = SaveBookRec(
                title=book[0],
                author=book[1],
                genre=book[2],
                description=book[3],
                cover_image_url=book[4]
            )
            db.session.add(save_newbookrec)  # Add the book to session
    '''
    for title, author, genre, description, cover_image_url in saved_bookrecs_data:
        # Check if the book already exists in the database
        if not SaveBookRec.query.filter_by(title=title, author=author).first():
            new_book = SaveBookRec(title=title, author=author, genre=genre, description=description, cover_image_url=cover_image_url)
            db.session.add(new_book)

    try: # Try to add the new book to the database
        #db.session.add(save_newbookrec)
        #db.session.add(new_book)
        db.session.commit() # Commit the changes to the database
    except Exception as e: # If an error occurs, rollback the changes and raise the error
        db.session.rollback() # Rollback the changes
        raise e # Raise the error

# Create the table before inserting data
with app.app_context():
    db.create_all()
    initSavedBookRecs() # Initialize the saved book recommendations