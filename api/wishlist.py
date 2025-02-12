from flask import Blueprint, jsonify, request
from __init__ import app, db  # Import db object from your Flask app's __init__.py
from model.librarydb import Book
from model.wishlist import Wishlist, update_wishlist_item  # Import the update function

# Create a Blueprint for the wishlist functionality
wishlist_api = Blueprint('wishlist_api', __name__, url_prefix='/api/wishlist')

# Route to get a dropdown list of books
@wishlist_api.route('/books', methods=['GET'])
def get_books():
    """Retrieve all books from the database to display in a dropdown menu."""
    books = Book.query.all()  # SQLAlchemy query to get all books from the books table
    books_list = [{'id': book.id, 'title': book.title, 'author': book.author} for book in books]
    return jsonify(books_list)

# Route to get all books in the wishlist 
@wishlist_api.route('/', methods=['GET'])
def get_wishlist():
    """Retrieve all books in the wishlist."""
    wishlist_items = Wishlist.query.all()  # Fetch all wishlist entries
    books_in_wishlist = []
    for item in wishlist_items:
        book = Book.query.get(item.book_id)
        if book:
            books_in_wishlist.append({'id': book.id, 'title': book.title, 'author': book.author})
    return jsonify(books_in_wishlist)

# Route to add a book to the wishlist
@wishlist_api.route('/', methods=['POST'])
def add_book_to_wishlist():
    """Add a book to the wishlist."""
    if request.is_json:
        data = request.get_json()
        book_id = data.get('book_id')

        # Validate that book_id is provided
        if not book_id:
            return jsonify({"error": "Missing book_id"}), 400

        # Check if the book exists in the books database
        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404

        # Check if the book is already in the wishlist
        existing_entry = Wishlist.query.filter_by(book_id=book_id).first()
        if existing_entry:
            return jsonify({"message": "Book already in wishlist"}), 200

        # Add the book to the wishlist
        new_entry = Wishlist(book_id=book_id)
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"message": "Book added to wishlist"}), 201

    return jsonify({"error": "Request must be JSON"}), 415

# Route to delete a book from the wishlist
@wishlist_api.route('/<int:book_id>', methods=['DELETE'])
def delete_book_from_wishlist(book_id):
    """Delete a book from the wishlist."""
    wishlist_item = Wishlist.query.filter_by(book_id=book_id).first()

    if not wishlist_item:
        return jsonify({"error": "Book not found in wishlist"}), 404

    try:
        db.session.delete(wishlist_item)
        db.session.commit()
        return jsonify({"message": "Book removed from wishlist"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Route to update a wishlist item
@wishlist_api.route('/<int:item_id>', methods=['PUT'])
def update_wishlist_item_route(item_id):
    """Update a wishlist item."""
    if request.is_json:
        data = request.get_json()
        new_book_id = data.get('book_id')

        # Validate that new_book_id is provided
        if not new_book_id:
            return jsonify({"error": "Missing book_id"}), 400

        # Check if the new book exists in the books database
        book = Book.query.get(new_book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404

        # Update the wishlist item
        result = update_wishlist_item(item_id, new_book_id)
        if "updated" in result:
            return jsonify({"message": result}), 200
        else:
            return jsonify({"error": result}), 404

    return jsonify({"error": "Request must be JSON"}), 415
