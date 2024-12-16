from flask import Blueprint, jsonify
from flask_cors import CORS
from flask_restful import Api
import sqlite3
import random

# Create the Blueprint for bookreview API
bookreview_api = Blueprint('bookreview_api', __name__, url_prefix='/api')
api = Api(bookreview_api)

# Enable CORS for this Blueprint
CORS(bookreview_api)

# Helper function to get a random book from the database
def get_random_book():
    conn = sqlite3.connect('books.db')  # Ensure this is the correct path to your database
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()
    return random.choice(books) if books else None

# Endpoint to get a random book
@bookreview_api.route('/random_book', methods=['GET'])  # Adjusted the route name to match what you're calling in `main.py`
def random_book():
    book = get_random_book()
    if book:
        return jsonify({
            'title': book[1],
            'author': book[2],
            'genre': book[3],
            'description': book[4],
            'image_cover': book[5]
        })
    else:
        return jsonify({'error': 'No books found'}), 404
