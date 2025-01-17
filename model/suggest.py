from __init__ import db, app
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.exc import IntegrityError
from model.librarydb import Book
import random

class SuggestedBook(db.Model):
    __tablename__ = 'suggestions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    author = db.Column(db.String, nullable=False)
    genre = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    cover_image_url = db.Column(db.String, nullable=True)

    def __init__(self, title, author, genre, description, cover_image_url):
        self.title = title
        self.author = author
        self.genre = genre
        self.description = description
        self.cover_image_url = cover_image_url

    def add_suggested_book(title, author, genre, description, cover_image_url):
        new_suggested_book = SuggestedBook(
            title=title,
            author=author,
            genre=genre,
            description=description,
            cover_image_url=cover_image_url
        )

        new_book = Book(
            title=title,
            author=author,
            genre=genre,
            description=description,
            cover_image_url=cover_image_url
        )

        try:
            db.session.add(new_suggested_book)
            db.session.add(new_book)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def __repr__(self):
        return f"<SuggestedBook {self.title}>"
    
    def get_random_suggested_book():
        try:
            suggested_books_query = SuggestedBook.query.all()
            return random.choice(suggested_books_query) if suggested_books_query else None
        except Exception as e:
            print(f"Error while fetching random book: {e}")
            return None
    
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
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "description": self.description,
            "cover_image_url": self.cover_image_url
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
        restored_books = {}

        for book_data in data:
            # Remove 'id' from the data if it exists (because id will be auto-generated)
            _ = book_data.pop('id', None)

            # Check if the book already exists based on title
            existing_book = SuggestedBook.query.filter_by(title=book_data.get("title")).first()
            if existing_book:
                # Update the existing book with new data
                existing_book.title = book_data.get('title', existing_book.title)
                existing_book.author = book_data.get('author', existing_book.author)
                existing_book.genre = book_data.get('genre', existing_book.genre)
                existing_book.description = book_data.get('description', existing_book.description)
                existing_book.cover_image_url = book_data.get('cover_image_url', existing_book.cover_image_url)
                db.session.commit()
                restored_books[existing_book.id] = existing_book
            else:
                # Create a new suggested book
                new_book = SuggestedBook(**book_data)
                new_book.create()
                restored_books[new_book.id] = new_book

        return restored_books

def initSuggest():
    with app.app_context():
        db.create_all()
        
    # tester data
    suggest_data = [
        SuggestedBook(title="The Hunger Games", author="Suzanne Collins", genre="Dystopian", description="The Hunger Games follows Katniss Everdeen as she is forced to fight in a yearly gladiatorial contest. Katniss's struggle and ultimate survival, along with Peeta Mellark's, sparks a revolution to overthrow the tyrannical Capitol.", cover_image_url="https://upload.wikimedia.org/wikipedia/en/d/dc/The_Hunger_Games.jpg"),
        SuggestedBook(title="Catch-22", author="Joseph Heller", genre="Classics", description="The work centres on Captain John Yossarian, an American bombardier stationed on a Mediterranean island during World War II, and chronicles his desperate attempts to stay alive.", cover_image_url="https://d28hgpri8am2if.cloudfront.net/book_images/cvr9781451621174_9781451621174_hr.jpg")
    ]

    for suggestion in suggest_data:
            try:
                if not Book.query.filter_by(title=suggestion.title).first() and not SuggestedBook.query.filter_by(title=suggestion.title).first():
                    db.session.add(suggestion)
                    db.session.commit()
            except IntegrityError:
                # Fails with bad or duplicate data
                db.session.rollback()

"""            
                    db.session.add(suggestion)
                    db.session.commit()
                    print(f"Record created: {repr(suggestion)}")
                else:
                    print(f"Book already exists: {suggestion.title}")
            except IntegrityError:
                # Rollback in case of error
                db.session.rollback()
                print(f"Error occurred while adding {suggestion.title}. Rolling back.")
            except Exception as e:
                db.session.rollback()
                print(f"Unexpected error: {str(e)}")
""" 