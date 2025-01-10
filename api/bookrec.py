from flask import Flask, jsonify, request, Blueprint
from flask_restful import Api
from model.librarydb import Book
from __init__ import app, db 
import random
import time

bookrec_api = Blueprint('bookrec_api', __name__, url_prefix='/api')
# API docs https://flask-restful.readthedocs.io/en/latest/ <-- just for reference
api = Api(bookrec_api)

# Helper function to get a random book from the database filtered by genre
def get_random_bookrec(genre=None):
    if genre:
        books = Book.query.filter(Book.genre.ilike(f'%{genre}%')).all() # Fetch a book from the requested genre
    else:
        books = Book.query.all() # Fetch all books if no genre is specified
    
    print(f"Books retrieved for genre '{genre}': {books}")  # Debug log

    return random.choice(books) if books else None # Return a random book if available

# Endpoint to get a random book
@bookrec_api.route('/random_bookrec', methods=['GET'])
def random_bookrec():
    genre = request.args.get('genre')  # Get the 'genre' parameter from the request
    print(f"Received genre: {genre}")  # Debug log
    
    while True:
        book = get_random_bookrec(genre)
        if book:
            return jsonify({
            'title': book.title,
            'author': book.author,
            'description': book.description,
            'image_cover': book.cover_image_url
            })
        else:
            print("No books found, retrying in 5 seconds...")
            time.sleep(5)
