## api, backend
from flask import Blueprint, request, jsonify, current_app, Response, g, Flask 
from flask_restful import Api, Resource  # used for REST API building
from __init__ import app, db
from model.librarydb import Book
from model.emotion import Emotion

emotion_api = Blueprint('emotion_api', __name__, url_prefix='/api/emotion')
api = Api(emotion_api)

# Create - Endpoint to add a reaction to a message
@emotion_api.route('', methods=['POST']) #{"user_id": 2, "title_id": "It", "author_id" : "Stephen King", "reaction_type": "🎉"}
def add_emotion():
    data = request.json

    user_id = data.get("user_id")
    reaction_type = data.get("reaction_type")
    title_id = data.get("title_id")
    author_id = data.get("author_id")

    try:
        # Create and add the message_reaction
        message_emotion = Emotion(reaction_type=reaction_type, user_id=user_id, title_id=title_id, author_id=author_id)
        message_emotion.create()
        return jsonify({'message': 'Emotion added successfully to post'}), 201
    except Exception as e:
        return jsonify({'error': 'Failed to add emotion', 'message': str(e)}), 500


@emotion_api.route('/books', methods=['GET'])
def get_books():
    """Retrieve all books from the database to display in a dropdown menu."""
    books = Book.query.all()  # SQLAlchemy query to get all books from the books table
    books_list = [{'id': book.id, 'title': book.title, 'author': book.author} for book in books]
    return jsonify(books_list)


# Read - Get all reactions for a specific book
@emotion_api.route('/<title_id>', methods=['GET'])   #/It
def get_emotion(title_id):
    try:
        # Query reactions for the specific book
        emotions = Emotion.query.filter_by(title_id=title_id).all()

        # Format the data to return
        emotion_data = [
            {
                'user_id': emo.user_id,
                'reaction_type': emo.reaction_type,
                'author_id': emo.author_id
            }
            for emo in emotions
        ]
        return jsonify({
            'title_id': title_id,
            'emotions': emotion_data
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get reactions', 'message': str(e)}), 500

# Read - Get all reactions for a specific user
@emotion_api.route('/user/<user_id>', methods=['GET'])   #/1
def get_user_emotion(user_id):
    try:
        # Query reactions for the specific user
        emotions = Emotion.query.filter_by(user_id=user_id).all()

        # Format the data to return
        emotion_data = [
            {
                'title_id': emo.title_id,
                'reaction_type': emo.reaction_type,
                'author_id': emo.author_id
            }
            for emo in emotions
        ]
        return jsonify({
            'user_id': user_id,
            'emotions': emotion_data
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get reactions', 'message': str(e)}), 500

# Update - Update a user's reaction on a post
@emotion_api.route('/update', methods=['PUT']) #{"user_id": 2, "title_id": "It", "reaction_type": "👍"}
def update_emotion():
    data = request.json
    print("Update Request Data:", data)  # Debugging
    user_id = data.get("user_id")
    title_id = data.get("title_id")
    new_reaction_type = data.get("reaction_type")

    # validate input
    if not user_id or not title_id or not new_reaction_type:
        return jsonify({"error": "All fields (user_id, title_id, reaction_type) are required"}), 400

    try:
        # Fetch the reaction from the database
        emotion = Emotion.query.filter_by(user_id=user_id, title_id=title_id).first()

        # If the reaction does not exist, return an error
        if not emotion:
            return jsonify({"error": "Reaction not found"}), 404

        # Update the reaction type
        emotion.reaction_type = new_reaction_type

        db.session.commit()

        return jsonify({
            "message": "Reaction updated successfully", 
            "reaction": {
                "user_id": emotion.user_id,
                "title_id": emotion.title_id,
                "reaction_type": emotion.reaction_type,
                "author_id": emotion.author_id
            }
        }), 200 
    except Exception as e:
        return jsonify({'error': 'Failed to update reaction', 'message': str(e)}), 500

# Delete - Remove a specific reaction
@emotion_api.route('/delete', methods=['DELETE']) #{"user_id": 2, "title_id": "It", "reaction_type": "👍", "author_id": "Stephen King"}
def delete_emotion():
    data = request.json
    print("Delete Request Data:", data)  # Debugging
    user_id = data.get("user_id")
    title_id = data.get("title_id")
    author_id = data.get("author_id")

    if not user_id or not title_id or not author_id:
        return jsonify({"error": "All fields (user_id, title_id, author_id) are required"}), 400

    # Query the Reaction model to find the reaction by user_id, title_id, and author_id
    emotion = Emotion.query.filter_by(user_id=user_id, title_id=title_id, author_id=author_id).first()

    if not emotion:
        return jsonify({"error": "Reaction not found"}), 404
    
    # Delete the reaction from the database
    db.session.delete(emotion)
    db.session.commit()

    return jsonify({"message": "Reaction deleted successfully"}), 200

# Delete - Reset all reactions for a specific user
@emotion_api.route('/reset_reactions/<user_id>', methods=['DELETE'])
def reset_emotion(user_id):
    try:
        # Query all reactions for the user
        emotions = Emotion.query.filter_by(user_id=user_id).all()

        if not emotions:
            return jsonify({"error": "No reactions found for this user"}), 404

        # Delete all reactions for the user
        for emotion in emotions:
            db.session.delete(emotion)

        db.session.commit()  # Commit the deletion

        return jsonify({"message": "All reactions for the user have been reset"}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to reset reactions', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)