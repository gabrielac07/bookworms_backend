from flask import Blueprint, request, jsonify, current_app, Response, g, Flask 
from flask_restful import Api, Resource  # used for REST API building
from __init__ import app
from model.reaction import Reaction

reaction_api = Blueprint('reaction_api', __name__, url_prefix='/api/reaction')
api = Api(reaction_api)


# In-memory data storage
messages = {}  # Example format: {"user_id": {"reactions": {"👍": 5, "❤️": 2}}}
emojis = ["👍", "❤️", "😂", "🎉", "😢", "😡"]

# Endpoint to add a reaction to a message
@reaction_api.route('', methods=['POST'])
def add_reaction():
    data = request.json

    user_id = data.get("user_id")
    reaction_type = data.get("reaction_type")
    post_id = data.get("post_id")

    '''
    try:
        # Create and add the message_reaction
        message_reaction = Reaction(user_id=user_id, reaction_type=reaction_type)
        message_reaction.create()
        return jsonify({'message': 'Reaction added successfully to post'}), 201
    except Exception as e:
        return jsonify({'error': 'Failed to add reaction', 'message': str(e)}), 500
    '''

    if not user_id or not reaction_type:
        return jsonify({"error": "Message ID and reaction are required"}), 400

    if reaction_type not in emojis:
        return jsonify({"error": f"reaction_type '{reaction_type}' not supported"}), 400

    # Initialize message reactions if not present
    if user_id not in messages:
        messages[user_id] = {"reaction_type": {}}

    # Update the reaction count
#    reactions = messages[user_id]["reactions"]
#    reactions[reaction] = reactions.get(reaction, 0) + 1
    reaction_type = Reaction(reaction_type=reaction_type, user_id=user_id, post_id=post_id)
    reaction_type.create()
    
    return jsonify({"message": "Reaction added successfully", "data": messages[user_id]}), 200

# Endpoint to get reactions for a specific message
# @reaction_api.route('/get_reactions/<user_id>', methods=['GET'])
# def get_reactions(user_id):
#     if user_id not in messages:
#         return jsonify({"error": "Message not found"}), 404

#     return jsonify({"user_id": user_id, "reactions": messages[user_id]["reactions"]}), 200

# Endpoint to get available emojis
@reaction_api.route('/get_emojis', methods=['GET'])
def get_emojis():
    return jsonify({"emojis": emojis}), 200

# Endpoint to add a custom emoji
@reaction_api.route('/add_emoji', methods=['POST'])
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
@reaction_api.route('/reset_reactions/<user_id>', methods=['DELETE'])
def reset_reactions(user_id):
    if user_id in messages:
        messages[user_id]["reactions"] = {}
        return jsonify({"message": "Reactions reset successfully"}), 200

    return jsonify({"error": "Message not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)