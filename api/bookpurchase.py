from flask import Blueprint, jsonify, request
from flask_restful import Api
from model.librarydb import Book  # Import your Book model
from __init__ import app, db  # Import Flask app and database instance
from model.bookpurchasedb import CartItem  # Import your CartItem model
from api.jwt_authorize import token_required, g

# Blueprint setup for the book purchase API
bookpurchase_api = Blueprint('bookpurchase_api', __name__, url_prefix='/api')
api = Api(bookpurchase_api)

# 1. Get all items in the cart (R)
@bookpurchase_api.route('/cart', methods=['GET'])
@token_required()
def get_cart():
    """Fetch all items in the cart along with total price and quantity."""
    items = CartItem.query.all()
    total_items = sum(item.quantity for item in items)
    total_price = sum(item.price * item.quantity for item in items)

    return jsonify({
        "items": [item.read() for item in items],  # Use read method from CartItem
        "total_items": total_items,
        "total_price": round(total_price, 2)
    })


# 2. Add an item to the cart (C)
@bookpurchase_api.route('/cart', methods=['POST'])
@token_required()
def add_to_cart_route():
    """Route wrapper to parse JSON and pass it to the logic function."""
    data = request.get_json()
    return add_to_cart(data)  # Now data is a physical parameter


def add_to_cart(data):
    """Add a new item to the cart or update the quantity if it already exists."""
    # Validate input data
    if not all(k in data for k in ('id', 'title', 'price', 'quantity', '_name')):
        return jsonify({"error": "All fields (id, title, price, quantity, _name) are required."}), 400

    # Check if item already exists in the cart
    item = CartItem.query.get(data['id'])
    if item:
        # If item exists, update quantity
        item.quantity += data['quantity']
    else:
        # Create a new cart item
        item = CartItem(
            id=data['id'],
            title=data['title'],
            price=data['price'],
            quantity=data['quantity'],
            username=data['_name']
        )
        db.session.add(item)

    # Save changes to the database
    db.session.commit()
    return jsonify({"message": "Item added to cart successfully."}), 201

# 3. Update an item's quantity in the cart (U)
@bookpurchase_api.route('/cart/<int:item_id>', methods=['PUT'])
@token_required()
def update_cart_item(item_id):
    """Update the quantity of a specific item in the cart."""
    data = request.get_json()

    # Ensure quantity is provided
    if 'quantity' not in data:
        return jsonify({"error": "Quantity is required."}), 400

    # Fetch the item from the cart
    item = CartItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found in the cart."}), 404

    # Ensure the quantity is valid
    if data['quantity'] <= 0:
        return jsonify({"error": "Quantity must be greater than zero."}), 400

    # Update the quantity
    item.quantity = data['quantity']
    db.session.commit()
    return jsonify({"message": "Item quantity updated successfully."})


# 4. Remove an item from the cart (D)
@bookpurchase_api.route('/cart/<int:item_id>', methods=['DELETE'])
@token_required()
def delete_cart_item(item_id):
    """Remove a specific item from the cart."""
    # Fetch the item by ID
    item = CartItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found in the cart."}), 404

    # Delete the item
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item removed from cart successfully."})


# 5. Clear the entire cart
@bookpurchase_api.route('/cart', methods=['DELETE'])
@token_required()
def clear_cart():
    """Clear all items from the cart."""
    # Delete all rows in the CartItem table
    CartItem.query.delete()
    db.session.commit()
    return jsonify({"message": "Cart cleared successfully."})