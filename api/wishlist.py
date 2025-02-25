from flask import Blueprint, jsonify, request, g
from __init__ import app, db  # Import db object from your Flask app's __init__.py
from model.librarydb import Book
from model.wishlist import Wishlist, update_wishlist_item, get_wishlist, add_to_wishlist, delete_from_wishlist  # Import the functions
from api.jwt_authorize import token_required
from model.user import User

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
@token_required()
def get_user_wishlist():
    """Retrieve all books in the user's wishlist."""
    current_user = g.current_user
    wishlist_items = get_wishlist(current_user._uid)  # Fetch all wishlist entries for the current user
    books_in_wishlist = []
    for item in wishlist_items:
        book = Book.query.get(item.book_id)
        if book:
            books_in_wishlist.append({
                'id': item.id,
                'book_id': book.id,
                'title': book.title,
                'author': book.author,
                'status': item.status,
                'date_added': item.date_added.strftime('%Y-%m-%d'),  # Format date to exclude time
                'availability': item.availability
            })
    return jsonify(books_in_wishlist)

# Route to add a book to the wishlist
@wishlist_api.route('/', methods=['POST'])
@token_required()
def add_book_to_wishlist():
    """Add a book to the user's wishlist."""
    current_user = g.current_user
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

        # Add the book to the user's wishlist
        result = add_to_wishlist(current_user._uid, book_id)
        if "added" in result:
            return jsonify({"message": result}), 201
        else:
            return jsonify({"error": result}), 400

    return jsonify({"error": "Request must be JSON"}), 415

# Route to delete a book from the wishlist
@wishlist_api.route('/<int:id>', methods=['DELETE'])
@token_required()
def delete_book_from_wishlist(id):
    """Delete a book from the user's wishlist."""
    current_user = g.current_user
    wishlist_item = Wishlist.query.get(id)

    if not wishlist_item or wishlist_item.user_uid != current_user._uid:
        return jsonify({"error": "Wishlist item not found"}), 404

    try:
        db.session.delete(wishlist_item)
        db.session.commit()
        return jsonify({"message": "Wishlist item removed"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Route to update a wishlist item
@wishlist_api.route('/<int:id>', methods=['PUT'])
@token_required()
def update_wishlist_item_route(id):
    """Update a wishlist item."""
    current_user = g.current_user
    wishlist_item = Wishlist.query.get(id)

    if not wishlist_item or wishlist_item.user_uid != current_user._uid:
        return jsonify({"error": "Wishlist item not found"}), 404

    if request.is_json:
        data = request.get_json()
        new_status = data.get('status')

        # Validate the new status
        if new_status not in ["for later", "in progress", "finished"]:
            return jsonify({"error": "Invalid status"}), 400

        # Update the wishlist item
        result = update_wishlist_item(id, new_status)
        if "updated" in result:
            return jsonify({"message": result}), 200
        else:
            return jsonify({"error": result}), 400

    return jsonify({"error": "Request must be JSON"}), 415

# Route to get availability of a book in the wishlist
@wishlist_api.route('/availability/<int:book_id>', methods=['GET'])
@token_required()
def get_book_availability(book_id):
    """Get the availability of a book in the user's wishlist."""
    current_user = g.current_user
    wishlist_item = Wishlist.query.filter_by(user_uid=current_user._uid, book_id=book_id).first()
    if wishlist_item:
        return jsonify({"availability": wishlist_item.availability}), 200
    else:
        return jsonify({"error": "Book not found in wishlist"}), 404

# Route to update availability of a book in the wishlist (admin only)
@wishlist_api.route('/availability/<int:item_id>', methods=['PUT'])
@token_required()
def update_book_availability(item_id):
    """Update the availability of a book in the wishlist (admin only)."""
    current_user = g.current_user

    if current_user.role != 'Admin':
        return {'message': 'Unauthorized.'}, 401

    if request.is_json:
        data = request.get_json()
        new_availability = data.get('availability')

        # Validate the new availability
        if new_availability not in ["available", "out of stock"]:
            return jsonify({"error": "Invalid availability"}), 400

        # Update the availability
        with app.app_context():
            try:
                item = Wishlist.query.get(item_id)
                if item:
                    item.availability = new_availability
                    db.session.commit()
                    return jsonify({"message": f"Wishlist item with id {item_id} updated to {new_availability}."}), 200
                else:
                    return jsonify({"error": "Wishlist item not found"}), 404
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    return jsonify({"error": "Request must be JSON"}), 415
