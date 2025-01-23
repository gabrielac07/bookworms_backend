from flask import Blueprint, request, jsonify, current_app, Response, g, Flask 
from flask_restful import Api, Resource  # used for REST API building
from __init__ import app, db
from model.reaction import Reaction

reaction_api = Blueprint('reaction_api', __name__, url_prefix='/api/reaction')
api = Api(reaction_api)


# In-memory data storage
messages = {}  # Example format: {"post_id": {"user_id": {"reaction_type": "👍"}}}
emojis = ["👍", "❤️", "😂", "🎉", "😢", "😡"]

# Create - Endpoint to add a reaction to a message
@reaction_api.route('', methods=['POST']) #{"user_id": 2, "post_id": 1, "reaction_type": "🎉"}
def add_reaction():
    data = request.json

    user_id = data.get("user_id")
    reaction_type = data.get("reaction_type")
    post_id = data.get("post_id")

    try:
        # Create and add the message_reaction
        message_reaction = Reaction(reaction_type=reaction_type, user_id=user_id, post_id=post_id)
        message_reaction.create()
        return jsonify({'message': 'Reaction added successfully to post'}), 201
    except Exception as e:
        return jsonify({'error': 'Failed to add reaction', 'message': str(e)}), 500
    
# Create - Endpoint to add a custom emoji
@reaction_api.route('/add_emoji', methods=['POST']) #{"emoji": "🔥"}
def add_emoji():
    data = request.json
    new_emoji = data.get("emoji")

    if not new_emoji:
        return jsonify({"error": "Emoji is required"}), 400

    if new_emoji in emojis:
        return jsonify({"error": "Emoji already exists"}), 400

    emojis.append(new_emoji)
    return jsonify({"message": "Emoji added successfully", "emojis": emojis}), 200

#Read - Get all available emojis
@reaction_api.route('/get_emojis', methods=['GET'])
def get_emojis():
    return jsonify({"emojis": emojis}), 200

# Read - Get all reactions for a specific post
@reaction_api.route('/<int:post_id>', methods=['GET'])
def get_reactions(post_id):
    try:
        # Query reactions for the specific post
        reactions = Reaction.query.filter_by(post_id=post_id).all()

        #Format the data to resturn
        reactions_data = [
            {
                'user_id': reaction.user_id,
                'reaction_type': reaction.reaction_type
            }
            for reaction in reactions
        ]
        return jsonify({
            'post_id': post_id,
            'reactions': reactions_data}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get reactions', 'message': str(e)}), 500

# Update - Update a user's reaction on a post
@reaction_api.route('/update', methods=['PUT']) #{"user_id": 2, "post_id": 1, "reaction_type": "👍"}
def update_reaction():
    data = request.json
    user_id = data.get("user_id")
    post_id = data.get("post_id")
    new_reaction_type = data.get("reaction_type")

    # validate input
    if not user_id or not post_id or not new_reaction_type:
        return jsonify({"error": "All fields (user_id, post_id, reaction_type) are required"}), 400

    if new_reaction_type not in emojis:
        return jsonify({"error": "Invalid emoji"}), 400

    try:
        # Fetch the reaction from the database
        reaction = Reaction.query.filter_by(user_id=user_id, post_id=post_id).first()

        # If the reaction does not exist, return an error
        if not reaction:
          return jsonify({"error": "Reaction not found"}), 404
       
       # Update the reaction type
        reaction.reaction_type = new_reaction_type

        db.session.commit()

        return jsonify({
            "message": "Reaction updated successfully", 
            "reaction":{
                "user_id": reaction.user_id,
                "post_id": reaction.post_id,
                "reaction_type": reaction.reaction_type
            }
            }), 200 
    except Exception as e:
        return jsonify({'error': 'Failed to update reaction', 'message': str(e)}), 500
  
# Delete - Remove a specific reaction
@reaction_api.route('/delete', methods=['DELETE']) #{"user_id": 2, "post_id": 1}
def delete_reaction():
    data = request.json
    user_id = data.get("user_id")
    post_id = data.get("post_id")

    if not user_id or not post_id:
        return jsonify({"error": "Both user_id and post_id are required"}), 400

    # Query the Reaction model to find the reaction by user_id and post_id
    reaction = Reaction.query.filter_by(user_id=user_id, post_id=post_id).first()

    if not reaction:
        return jsonify({"error": "Reaction not found"}), 404
    
    # Delete the reaction from te database
    db.session.delete(reaction)
    db.session.commit()

    return jsonify({"message": "Reaction deleted successfully"}), 200

# Delete - Reset all reactions for a specific post
@reaction_api.route('/reset_reactions/<post_id>', methods=['DELETE']) #/1
def reset_reactions(post_id):
    #Query all reactions for the post
    reactions = Reaction.query.filter_by(post_id=post_id).all()

    if not reactions:
        return jsonify({"error": "No reactions found for this post"}), 404
   
   # Dedlete all reactions for the post
    for reaction in reactions:
        db.session.delete(reaction)

    db.session.commit() # Commit the deletetion

if __name__ == '__main__':
    app.run(debug=True)