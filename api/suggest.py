from flask import Blueprint, request, jsonify
from flask_restful import Api
from model.librarydb import Book
from model.suggest import SuggestedBook
from __init__ import db

# Define Blueprint and Api
suggest_api = Blueprint('suggest_api', __name__, url_prefix='/api/suggest')
api = Api(suggest_api)

# Endpoint to add suggested books (Create)
@suggest_api.route('', methods=['POST'])  
def add_book():
    if not request.json or 'title' not in request.json:
        return jsonify({'error': 'Title is required to create the book'}), 400
    data = request.json

    title = data.get('title')
    author = data.get('author')
    genre = data.get('genre')
    description = data.get('description')
    cover_url = data.get('cover_url')

    try:
        # Create and add the suggested book
        suggested_book = SuggestedBook(title=title, author=author, genre=genre, description=description, cover_url=cover_url)
        suggested_book.create()
        return jsonify({'message': 'Book added successfully to suggestions'}), 201
    except Exception as e:
        return jsonify({'error': 'Failed to add book', 'message': str(e)}), 500

# Add multiple suggested books (Create)
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
        cover_url = book_data.get('cover_url')

        try:
            # Create and add the suggested book
            suggested_book = SuggestedBook(title=title, author=author, genre=genre, description=description, cover_url=cover_url)
            suggested_book.create()
            results.append({'message': f'Book {title} added successfully to suggestions', 'title': title})
        except Exception as e:
            results.append({'error': f'Failed to add book {title}', 'message': str(e), 'title': title})

    return jsonify(results), 201

# Endpoint to fetch a random suggested book (Read)
@suggest_api.route('/book', methods=['GET'])
def get_suggestion():
    try:
        # Query all suggested books
        books = SuggestedBook.query.all()

        # Convert the list of book objects to a list of dictionaries
        books_data = [
            {
                'title': book.title,
                'author': book.author,
                'genre': book.genre,
                'description': book.description,
                'cover_url': book.cover_url
            }
            for book in books
        ]

        return jsonify(books_data), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch books', 'message': str(e)}), 500

# Endpoint to fetch a random suggested book (Read)
@suggest_api.route('/random', methods=['GET'])
def random_book():
    book = SuggestedBook.get_random_suggested_book()
    if book:
        return jsonify({
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'description': book.description,
            'cover_url': book.cover_url
        })
    else:
        return jsonify({'error': 'No books found'}), 404
    
# Endpoint to update existing suggested book (Update)
@suggest_api.route('', methods=['PUT'])
def update_book():
    data = request.json

    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title is required to update the book'}), 400

    try:
        # Fetch the existing book by title
        suggested_book = SuggestedBook.query.filter_by(title=title).first()
        if not suggested_book:
            return jsonify({'error': 'Book not found'}), 404

        # Update the book details
        suggested_book.title = data.get('title', suggested_book.title)
        suggested_book.author = data.get('author', suggested_book.author)
        suggested_book.genre = data.get('genre', suggested_book.genre)
        suggested_book.description = data.get('description', suggested_book.description)
        suggested_book.cover_url = data.get('cover_url', suggested_book.cover_url)

        suggested_book.update() 
        return jsonify({'message': 'Book updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update book', 'message': str(e)}), 500

# Endpoint to delete  suggested book (Delete)
@suggest_api.route('', methods=['DELETE'])
def delete_book():
    data = request.json
    
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title is required to delete the book'}), 400

    try:
        suggested_book = SuggestedBook.query.filter_by(title=title).first()
        
        if not suggested_book:
            return jsonify({'error': 'Book not found'}), 404
        
        db.session.delete(suggested_book)
        db.session.commit()
        
        return jsonify({'message': 'Book deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to delete book', 'message': str(e)}), 500
