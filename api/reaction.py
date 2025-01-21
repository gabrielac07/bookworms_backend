from flask import Blueprint, request, jsonify, current_app, Response, g, Flask 
from flask_restful import Api, Resource  # used for REST API building
from __init__ import app

reaction_api = Blueprint('reaction_api', __name__, url_prefix='/api')


# In-memory data storage
messages = {}  # Example format: {"message_id": {"reactions": {"👍": 5, "❤️": 2}}}
emojis = ["👍", "❤️", "😂", "🎉", "😢", "😡"]

# Endpoint to add a reaction to a message
@app.route('/add_reaction', methods=['POST'])
def add_reaction():
    data = request.json
    message_id = data.get("message_id")
    reaction = data.get("reaction")

    if not message_id or not reaction:
        return jsonify({"error": "Message ID and reaction are required"}), 400

    if reaction not in emojis:
        return jsonify({"error": f"Reaction '{reaction}' not supported"}), 400

    # Initialize message reactions if not present
    if message_id not in messages:
        messages[message_id] = {"reactions": {}}

    # Update the reaction count
    reactions = messages[message_id]["reactions"]
    reactions[reaction] = reactions.get(reaction, 0) + 1

    return jsonify({"message": "Reaction added successfully", "data": messages[message_id]}), 200

# Endpoint to get reactions for a specific message
@app.route('/get_reactions/<message_id>', methods=['GET'])
def get_reactions(message_id):
    if message_id not in messages:
        return jsonify({"error": "Message not found"}), 404

    return jsonify({"message_id": message_id, "reactions": messages[message_id]["reactions"]}), 200

# Endpoint to get available emojis
@app.route('/get_emojis', methods=['GET'])
def get_emojis():
    return jsonify({"emojis": emojis}), 200

# Endpoint to add a custom emoji
@app.route('/add_emoji', methods=['POST'])
def add_emoji():
    data = request.json
    new_emoji = data.get("emoji")

    if not new_emoji:
        return jsonify({"error": "Emoji is required"}), 400

    if new_emoji in emojis:
        return jsonify({"error": "Emoji already exists"}), 400

    emojis.append(new_emoji)
    return jsonify({"message": "Emoji added successfully", "emojis": emojis}), 200

# Endpoint to reset reactions for a message
@app.route('/reset_reactions/<message_id>', methods=['DELETE'])
def reset_reactions(message_id):
    if message_id in messages:
        messages[message_id]["reactions"] = {}
        return jsonify({"message": "Reactions reset successfully"}), 200

    return jsonify({"error": "Message not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)