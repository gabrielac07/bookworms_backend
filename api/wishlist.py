from flask import Blueprint, jsonify, request
from __init__ import app, db  # Import db object from your Flask app's __init__.py
from model.librarydb import Book
from model.wishlist import Wishlist

# Create a Blueprint for the wishlist functionality
wishlist_api = Blueprint('wishlist_api', __name__, url_prefix='/api/wishlist')

# Static user ID for all operations
STATIC_USER_ID = 4

# Route to get a dropdown list of books
@wishlist_api.route('/books', methods=['GET'])
def get_books():
    """Retrieve all books from the database to display in a dropdown menu."""
    books = Book.query.all()
    books_list = [{'id': book.id, 'title': book.title, 'author': book.author} for book in books]
    return jsonify(books_list)

# Route to get all books in the wishlist for the static user
@wishlist_api.route('/', methods=['GET'])
def get_wishlist():
    """Retrieve all books in the wishlist for the static user."""
    wishlist_items = Wishlist.query.filter_by(user_id=STATIC_USER_ID).all()
    books_in_wishlist = []
    for item in wishlist_items:
        book = Book.query.get(item.book_id)
        if book:
            books_in_wishlist.append({'id': book.id, 'title': book.title, 'author': book.author})
    return jsonify(books_in_wishlist)

# Route to add a book to the wishlist for the static user
@wishlist_api.route('/', methods=['POST'])
def add_book_to_wishlist():
    """Add a book to the wishlist for the static user."""
    if request.is_json:
        data = request.get_json()
        book_id = data.get('book_id')

        # Validate that the book_id is provided
        if not book_id:
            return jsonify({"error": "Missing book_id"}), 400

        # Check if the book exists in the books database
        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404

        # Check if the book is already in the user's wishlist
        existing_entry = Wishlist.query.filter_by(user_id=STATIC_USER_ID, book_id=book_id).first()
        if existing_entry:
            return jsonify({"message": "Book already in wishlist"}), 200

        # Add the book to the wishlist
        new_entry = Wishlist(user_id=STATIC_USER_ID, book_id=book_id)
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"message": "Book added to wishlist"}), 201

    return jsonify({"error": "Request must be JSON"}), 415

# Route to delete a book from the wishlist for the static user
@wishlist_api.route('/<int:book_id>', methods=['DELETE'])
def delete_book_from_wishlist(book_id):
    """Delete a book from the wishlist for the static user."""
    wishlist_item = Wishlist.query.filter_by(user_id=STATIC_USER_ID, book_id=book_id).first()

    if not wishlist_item:
        return jsonify({"error": "Book not found in wishlist"}), 404

    try:
        db.session.delete(wishlist_item)
        db.session.commit()
        return jsonify({"message": "Book removed from wishlist"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
