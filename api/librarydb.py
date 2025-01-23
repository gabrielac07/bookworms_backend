from flask import Blueprint, request, jsonify
from flask_restful import Api
from model.librarydb import Book
from __init__ import db

# Define Blueprint and Api
library_api = Blueprint('library_api', __name__, url_prefix='/api/library')
api = Api(library_api)

@library_api.route('', methods=['POST'])  
def add_book():
    data = request.json
    if data is None:
        return jsonify({'error': 'Invalid JSON'}), 400

    title = data.get('title')
    author = data.get('author')
    genre = data.get('genre')
    description = data.get('description')
    cover_image_url = data.get('cover_image_url')

    try:
        # Create and add the suggested book
        book = Book(title=title, author=author, genre=genre, description=description, cover_image_url=cover_image_url)
        book.create()
        return jsonify({'message': 'Book added successfully to books'}), 201
    except Exception as e:
        return jsonify({'error': 'Failed to add book to books', 'message': str(e)}), 500