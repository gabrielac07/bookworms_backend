import sqlite3
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Base class for defining the database models
Base = declarative_base()

class Book(Base):
    """
    Represents a book in the database.

    Attributes:
        id (int): The primary key, auto-incremented.
        title (str): The title of the book.
        author (str): The author of the book.
        genre (str): The genre of the book.
        description (str): A brief description of the book.
        image_cover (str): A URL to the book's cover image.
    """
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image_cover = Column(String, nullable=True)


def create_database(engine_url="sqlite:///recbooks.db"):
    """
    Creates the database and the 'books' table if they do not already exist.

    Args:
        engine_url (str): The database URL (default is an SQLite database named 'recbooks.db').
    """
    engine = create_engine(engine_url)
    Base.metadata.create_all(engine)  # Creates all tables defined in the Base class


def get_session(engine_url="sqlite:///recbooks.db"):
    """
    Creates a session for interacting with the database.

    Args:
        engine_url (str): The database URL (default is an SQLite database named 'recbooks.db').

    Returns:
        Session: A session object for querying and modifying the database.
    """
    engine = create_engine(engine_url)
    Session = sessionmaker(bind=engine)
    return Session()


def insert_book(session, title, author, genre, description, image_cover):
    """
    Inserts a new book into the 'books' table.

    Args:
        session (Session): Active SQLAlchemy session.
        title (str): The title of the book.
        author (str): The author of the book.
        genre (str): The genre of the book.
        description (str): A brief description of the book.
        image_cover (str): A URL to the book's cover image.
    """
    new_book = Book(
        title=title,
        author=author,
        genre=genre,
        description=description,
        image_cover=image_cover,
    )
    session.add(new_book)
    session.commit()


def get_all_books(session):
    """
    Retrieves all books from the 'books' table.

    Args:
        session (Session): An active SQLAlchemy session.

    Returns:
        list: A list of all books in the database. Each book is represented as a Book object.
    """
    return session.query(Book).all()


# --- Example usage ---
if __name__ == "__main__":
    # Step 1: Create the database and table
    create_database()

    # Step 2: Establish a session
    session = get_session()

    # Step 3: Insert sample books
    insert_book(
        session,
        "Great Expectations",
        "Charles Dickens",
        "Classics",
        "Great Expectations follows the childhood and young adult years of Pip, a blacksmith's apprentice in a country village.",
        "https://m.media-amazon.com/images/I/715lBsaI4sL.jpg",
    )
    insert_book(
        session,
        "The Outsiders",
        "S.E. Hinton",
        "Classics",
        "Ponyboy, a greaser from the 'wrong' side of town, struggles to find his place in society alongside his friends after personal tragedies.",
        "https://m.media-amazon.com/images/I/71Bg39CmhoL.jpg",
    )

    # Step 4: Retrieve and print all books
    books = get_all_books(session)
    for book in books:
        print(
            f"ID: {book.id}, Title: {book.title}, Author: {book.author}, Genre: {book.genre}, "
            f"Description: {book.description}, Cover: {book.image_cover}"
        )
