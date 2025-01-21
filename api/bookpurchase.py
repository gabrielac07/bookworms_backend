from flask import Blueprint, jsonify, request
from flask_restful import Api
from model.librarydb import Book  
import random
from __init__ import app, db
from model.bookpurchasedb import CartItem 

# Avika please ADD COMMENTS because otherwise you're going to forget wth you're doing
bookpurchase_api = Blueprint('bookpurchase_api', __name__, url_prefix='/api')
api = Api(bookpurchase_api)

# Get all items in the cart
@app.route('/cart', methods=['GET'])
def get_cart():
    items = CartItem.query.all()
    total_items = sum(item.quantity for item in items)
    total_price = sum(item.price * item.quantity for item in items)

    return jsonify({
        "items": [item.to_dict() for item in items],
        "total_items": total_items,
        "total_price": round(total_price, 2)
    })

# Add an item to the cart
@app.route('/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    if not all(k in data for k in ('id', 'title', 'price', 'quantity', '_name')):
        return jsonify({"error": "All fields (id, title, price, quantity, _name) are required."}), 400

    item = CartItem.query.get(data['id'])
    if item:
        item.quantity += data['quantity']
    else:
        item = CartItem(
            id=data['id'],
            title=data['title'],
            price=data['price'],
            quantity=data['quantity'],
            username=data['_name']
        )
        db.session.add(item)

    db.session.commit()
    return jsonify({"message": "Item added to cart successfully."}), 201

# Update an item's quantity in the cart
@app.route('/cart/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    data = request.get_json()
    if 'quantity' not in data:
        return jsonify({"error": "Quantity is required."}), 400

    item = CartItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found in the cart."}), 404

    if data['quantity'] <= 0:
        return jsonify({"error": "Quantity must be greater than zero."}), 400

    item.quantity = data['quantity']
    db.session.commit()
    return jsonify({"message": "Item quantity updated successfully."})

# Remove an item from the cart
@app.route('/cart/<int:item_id>', methods=['DELETE'])
def delete_cart_item(item_id):
    item = CartItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found in the cart."}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item removed from cart successfully."})

# Clear the entire cart
@app.route('/cart', methods=['DELETE'])
def clear_cart():
    CartItem.query.delete()
    db.session.commit()
    return jsonify({"message": "Cart cleared successfully."})