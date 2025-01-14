from flask import Blueprint, request, jsonify
from flask_restful import Api
from model.librarydb import Book
from model.suggest import SuggestedBook, add_suggested_book, get_random_suggested_book
from __init__ import db

# Define Blueprint and Api
suggest_api = Blueprint('suggest_api', __name__, url_prefix='/api/suggest')
api = Api(suggest_api)

# Endpoint to add suggested books
@suggest_api.route('', methods=['POST'])  
def add_book():
    data = request.json  # Expecting JSON data

    title = data.get('title')
    author = data.get('author')
    genre = data.get('genre')
    description = data.get('description')
    cover_image_url = data.get('cover_image_url')

    try:
        # Add book to suggestions and books table
        add_suggested_book(title, author, genre, description, cover_image_url)
        return jsonify({'message': 'Book added successfully to both suggestions and books tables'}), 201
    except Exception as e:
        return jsonify({'error': 'Failed to add book'}), 500

# Endpoint to fetch a random suggested book
@suggest_api.route('/random', methods=['GET'])
def random_book():
    book = get_random_suggested_book()
    if book:
        return jsonify({
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'description': book.description,
            'image_cover': book.cover_image_url
        })
    else:
        return jsonify({'error': 'No books found'}), 404