from __init__ import db
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.exc import IntegrityError
from model.librarydb import Book
import random

class SuggestedBook(db.Model):
    __tablename__ = 'suggestions'
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

def get_random_suggested_book():
    try:
        suggested_books_query = SuggestedBook.query.all()
        return random.choice(suggested_books_query) if suggested_books_query else None
    except Exception as e:
        print(f"Error while fetching random book: {e}")
        return None