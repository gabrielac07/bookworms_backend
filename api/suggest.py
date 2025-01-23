from flask import Blueprint, request, jsonify
from flask_restful import Api
from model.librarydb import Book
from model.suggest import SuggestedBook
from __init__ import db

# Define Blueprint and Api
suggest_api = Blueprint('suggest_api', __name__, url_prefix='/api/suggest')
api = Api(suggest_api)

# Endpoint to add suggested books
@suggest_api.route('', methods=['POST'])  
def add_book():
    data = request.json

    title = data.get('title')
    author = data.get('author')
    genre = data.get('genre')
    description = data.get('description')
    cover_image_url = data.get('cover_image_url')

    try:
        # Create and add the suggested book
        suggested_book = SuggestedBook(title=title, author=author, genre=genre, description=description, cover_image_url=cover_image_url)
        suggested_book.create()
        return jsonify({'message': 'Book added successfully to suggestions'}), 201
    except Exception as e:
        return jsonify({'error': 'Failed to add book', 'message': str(e)}), 500

@suggest_api.route('/bulk', methods=['POST'])
def add_books_bulk():
    data = request.json

    if not isinstance(data, list):
        return jsonify({'error': 'Expected a list of books'}), 400

    results = []

    for book_data in data:
        title = book_data.get('title')
        author = book_data.get('author')
        genre = book_data.get('genre')
        description = book_data.get('description')
        cover_image_url = book_data.get('cover_image_url')

        try:
            # Create and add the suggested book
            suggested_book = SuggestedBook(title=title, author=author, genre=genre, description=description, cover_image_url=cover_image_url)
            suggested_book.create()
            results.append({'message': f'Book {title} added successfully to suggestions', 'title': title})
        except Exception as e:
            results.append({'error': f'Failed to add book {title}', 'message': str(e), 'title': title})

    return jsonify(results), 201

# Endpoint to fetch a random suggested book
@suggest_api.route('/random', methods=['GET'])
def random_book():
    book = SuggestedBook.get_random_suggested_book()
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