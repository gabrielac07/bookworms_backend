from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.exc import IntegrityError
from __init__ import db, app
from model.librarydb import Book
#import random

class SaveBookRec(db.Model): # Class to save a book recommendation
    __tablename__ = 'savedbookrecs' # name of the table
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    cover_url = Column(String, nullable=True)

    def __init__(self, title, author, genre, description, cover_url): # Constructor to initialize the book recommendation
        self.title = title
        self.author = author
        self.genre = genre
        self.description = description
        self.cover_url = cover_url
    
    def read(self): # Function to read the book recommendation
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'genre': self.genre,
            'description': self.description,
            'cover_url': self.cover_url
        }

    @classmethod # Class method to restore the book recommendation
    def restore(cls, data):
        for item in data:
            existing_record = cls.query.filter_by(title=item['title'], author=item['author']).first()
            if existing_record:
                existing_record.genre = item['genre']
                existing_record.description = item['description']
                existing_record.cover_url = item['cover_url']
            else: # If the book recommendation does not exist, create a new record
                new_record = cls( # Create a new record
                    title=item['title'],
                    author=item['author'],
                    genre=item['genre'],
                    description=item['description'],
                    cover_url=item['cover_url']
                )
                db.session.add(new_record)
        db.session.commit()
        return cls.query.all() # Return all book recommendations

# Static data
def initSavedBookRecs(): 
    saved_bookrecs_data = [
        ("A Clash of Kings", "George R. R. Martin", "Fantasy", "A Clash of Kings by George R. R. Martin is the second installment in the A Song of Ice and Fire series. The novel follows the chaos and power struggles that erupt across the Seven Kingdoms as multiple factions claim the Iron Throne following the death of King Robert Baratheon. Amid the political intrigue and battles, dark supernatural forces begin to rise, threatening the realm from the shadows.", "https://m.media-amazon.com/images/I/81ES5DAxprL.jpg"),
        ("A Storm of Swords", "George R. R. Martin", "Fantasy", "A Storm of Swords by George R. R. Martin is the third book in the A Song of Ice and Fire series. The novel continues the epic tale of political intrigue, betrayal, and warfare in the Seven Kingdoms. As the War of the Five Kings rages on, alliances are forged and broken, and the fate of Westeros hangs in the balance.", "https://m.media-amazon.com/images/I/819o5XLwuFL.jpg"),
        #("A Feast for Crows", "George R. R. Martin", "Fantasy", "A Feast for Crows by George R. R. Martin is the fourth book in the A Song of Ice and Fire series. The novel follows the aftermath of the War of the Five Kings as the Seven Kingdoms struggle to recover from the devastation and chaos. As new threats emerge and old rivalries resurface, the realm faces an uncertain future.", "https://m.media-amazon.com/images/I/91Tpg6BX00L._UF1000,1000_QL80_.jpg")
    ]

    for title, author, genre, description, cover_url in saved_bookrecs_data:
        try:
            if not SaveBookRec.query.filter_by(title=title, author=author).first():
                new_book = SaveBookRec(title=title, author=author, genre=genre, description=description, cover_url=cover_url)
                db.session.add(new_book)
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing book: {e}")
    db.session.commit()

# Create the table before inserting data
with app.app_context():
    db.create_all()
    initSavedBookRecs() # Initialize the saved book recommendations

'''
    def add_bookrec(title, author, genre, description, cover_url):
        new_bookrec = SaveBookRec( # Create a new book recommendation object
            title=title,
            author=author,
            genre=genre,
            description=description,
            cover_url=cover_url
        )

        new_book = Book( # Create a new book object
            title=title,
            author=author,
            genre=genre,
            description=description,
            cover_url=cover_url
        )

        try:
            db.session.add(new_bookrec)
            db.session.add(new_book)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def __repr__(self):
        return f"<SaveBookRec {self.title}>"
    
    def update(self): # Function to update the book recommendation
        """
        The update method commits the transaction to the database.
        
        Uses: The db ORM method to commit the transaction.
        """
        try: # Try to update the book recommendation
            db.session.add(self) # Add the book recommendation to the session
            db.session.commit() 
        except Exception as e:  # If an error occurs, rollback the changes
            db.session.rollback()
            raise e
    
    def delete(self): # Function to delete the book recommendation
        """
        The delete method removes the object from the database and commits the transaction.
        
        Uses: The db ORM methods to delete and commit the transaction.
        """    
        try: # Try to delete the book recommendation
            db.session.delete(self)
            db.session.commit()
        except Exception as e: # If an error occurs, rollback the changes
            db.session.rollback()
        raise Exception(f"An error occurred while deleting the object: {str(e)}") from e
'''
