from flask import Blueprint, jsonify, request, g
from .jwt_authorize import token_required
from __init__ import db  # Import db object from your Flask app's __init__.py
from model.librarydb import Book
from model.wishlist import Wishlist

# Create a Blueprint for the wishlist functionality
wishlist_api = Blueprint('wishlist_api', __name__, url_prefix='/api/wishlist')

# Route to handle CORS preflight requests
@wishlist_api.route('/', methods=['OPTIONS'])
def handle_options():
    """Handle CORS preflight request"""
    response = jsonify({})
    response.status_code = 200
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# Ensure proper CORS headers for all routes
@wishlist_api.after_request
def after_request(response):
    """Ensure CORS headers are applied to all responses."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# Error handler to ensure CORS headers are included in error responses
@wishlist_api.errorhandler(Exception)
def handle_exception(e):
    """Handle exceptions and ensure CORS headers are included in error responses."""
    response = jsonify({"error": str(e)})
    response.status_code = getattr(e, 'code', 500)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# Route to get a dropdown list of books
@wishlist_api.route('/books', methods=['GET'])
def get_books():
    """Retrieve all books from the database to display in a dropdown menu."""
    books = Book.query.all()
    books_list = [{'id': book.id, 'title': book.title, 'author': book.author} for book in books]
    return jsonify(books_list)

# Route to get all books in the wishlist for a specific user
@wishlist_api.route('/', methods=['GET'])
@token_required  # Protect the route with token_required decorator
def get_user_wishlist():
    """Retrieve all books in the wishlist for a specific user."""
    current_user = g.current_user  # Access the current_user set by token_required

    wishlist_items = Wishlist.query.filter_by(_uid=current_user._uid).all()
    books_in_wishlist = []
    for item in wishlist_items:
        book = Book.query.get(item.book_id)
        if book:
            books_in_wishlist.append({'id': book.id, 'title': book.title, 'author': book.author})
    return jsonify(books_in_wishlist)

# Route to add a book to the wishlist for a specific user
@wishlist_api.route('/add', methods=['POST'])
@token_required  # Protect the route with token_required decorator
def add_book_to_user_wishlist():
    """Add a book to the wishlist for a specific user."""
    if request.is_json:
        data = request.get_json()
        book_id = data.get('book_id')

        # Validate that book_id is provided
        if not book_id:
            return jsonify({"error": "Missing book_id"}), 400

        # Get the current user from g.current_user
        current_user = g.current_user

        # Check if the book exists in the books database
        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404

        # Check if the book is already in the user's wishlist
        existing_entry = Wishlist.query.filter_by(_uid=current_user._uid, book_id=book_id).first()
        if existing_entry:
            return jsonify({"message": "Book already in wishlist"}), 200

        # Add the book to the wishlist
        new_entry = Wishlist(_uid=current_user._uid, book_id=book_id)
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"message": "Book added to wishlist"}), 201

    return jsonify({"error": "Request must be JSON"}), 415

# Route to delete a book from the wishlist for a specific user
@wishlist_api.route('/delete/<int:book_id>', methods=['DELETE'])
@token_required  # Protect the route with token_required decorator
def delete_book_from_user_wishlist(book_id):
    """Delete a book from the wishlist for a specific user."""
    # Get the current user from g.current_user
    current_user = g.current_user

    wishlist_item = Wishlist.query.filter_by(_uid=current_user._uid, book_id=book_id).first()

    if not wishlist_item:
        return jsonify({"error": "Book not found in wishlist"}), 404

    try:
        db.session.delete(wishlist_item)
        db.session.commit()
        return jsonify({"message": "Book removed from wishlist"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
