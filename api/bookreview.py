from flask import Blueprint, jsonify
from flask_restful import Api
from model.librarydb import Book  
import random
from __init__ import app, db 

# Soumini please ADD COMMENTS because otherwise you're going to forget wth you're doing
bookreview_api = Blueprint('bookreview_api', __name__, url_prefix='/api')
api = Api(bookreview_api)

def get_random_book():
    try:
        # Query all books
        books_query = Book.query.all()  # Fetch all books from the database
        if books_query:
            return random.choice(books_query)  # Pick a random book if books are available
        else:
            return None  # Returns none if no books are found
    except Exception as e:
        print(f"Error while fetching random book: {e}")
        return None

@bookreview_api.route('/random_book', methods=['GET'])
def random_book():
    book = get_random_book()
    if book:
        # If a random book is found, return its details as JSON
        return jsonify({
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'description': book.description,
            'image_cover': book.cover_image_url
        })
    else:
        # If no book is found, return an error message 
        return jsonify({'error': 'No books found'}), 404