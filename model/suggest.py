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
    cover_url = db.Column(db.String, nullable=True)

    def __init__(self, title, author, genre, description, cover_url):
        self.title = title
        self.author = author
        self.genre = genre
        self.description = description
        self.cover_url = cover_url

    def add_suggested_book(title, author, genre, description, cover_url):
        new_suggested_book = SuggestedBook(
            title=title,
            author=author,
            genre=genre,
            description=description,
            cover_url=cover_url
        )

        new_book = Book(
            title=title,
            author=author,
            genre=genre,
            description=description,
            cover_url=cover_url
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
            "cover_url": self.cover_url
        }
        
    def update(self):
        """
        The update method commits the transaction to the database.
        
        Uses:
            The db ORM method to commit the transaction.
        
        Raises:
            Exception: An error occurred when updating the object in the database.
        """
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    
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
        raise Exception(f"An error occurred while deleting the object: {str(e)}") from e
    
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
                existing_book.cover_url = book_data.get('cover_url', existing_book.cover_url)
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
        SuggestedBook(title="The Raven Boys", author="Maggie Stiefvater", genre="Fantasy", description="A young adult fantasy novel about a girl from a family of clairvoyants, the boys she befriends, and how their lives are intertwined along their journey to wake a slumbering king.", cover_url="https://m.media-amazon.com/images/I/71s5v4HfFjL._AC_UF1000,1000_QL80_.jpg"),
        SuggestedBook(title="Catch-22", author="Joseph Heller", genre="Classics", description="The work centres on Captain John Yossarian, an American bombardier stationed on a Mediterranean island during World War II, and chronicles his desperate attempts to stay alive.", cover_url="https://d28hgpri8am2if.cloudfront.net/book_images/cvr9781451621174_9781451621174_hr.jpg"),
        SuggestedBook(title="A Midsummer Night\'s Dream", author="William Shakespeare", genre="Classics", description="Four Athenians run away to the forest only to have Puck the fairy make both of the boys fall in love with the same girl.", cover_url="https://www.amazon.com/Midsummer-Nights-Dream-WILLIAM-SHAKESPEARE/dp/8175994509"),
        SuggestedBook(title="Never Let Me Go", author="Kazuo Ishiguro", genre="Mystery", description="Never Let Me Go follows students\' lives at an elite boarding school. The story explores themes of friendship, memories, and what it means to be human, gradually revealing deeper mysteries about the nature of their world.", cover_url="https://images.penguinrandomhouse.com/cover/9781400078776"),        
        SuggestedBook(title="A Deadly Education", author="Naomi Novik", genre="Fantasy", description="A Deadly Education is a 2020 fantasy novel written by American author Naomi Novik following Galadriel \"El\" Higgins, a half-Welsh, half-Indian sorceress, who must survive to graduation while controlling her destructive abilities at a school of magic very loosely inspired by the legend of the Scholomance.", cover_url="https://m.media-amazon.com/images/I/81j2VmcrS-L._AC_UF1000,1000_QL80_.jpg"),
        SuggestedBook(title="House of Leaves", author="Mark Z. Danielewski", genre="Suspense/Thriller", description="The House of Leaves synopsis details a story about a young man who finds a manuscript about a family's documentary, The Navidson Record, which details their experiences with a strange house.", cover_url="https://images.penguinrandomhouse.com/cover/9780375420528"),        
            
    ]

    for suggestion in suggest_data:
            try:
                if not Book.query.filter_by(title=suggestion.title).first() and not SuggestedBook.query.filter_by(title=suggestion.title).first():
                    db.session.add(suggestion)
                    db.session.commit()
            except IntegrityError:
                # Fails with bad or duplicate data
                db.session.rollback()