from flask import Flask, jsonify, request, Blueprint
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from __init__ import app, db 
import random
import time

app = Flask('bookrec_api')
CORS(app)  # Enable CORS for all routes

bookrec_api = Blueprint('bookrec_api', __name__,
                   url_prefix='/api')

# API docs https://flask-restful.readthedocs.io/en/latest/
api = Api(bookrec_api)

# Define the Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    genre = db.Column(db.String(50))
    description = db.Column(db.String(500))
    cover_image_url = db.Column(db.String(200))

    def to_dict(self):
        return {
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'cover_image_url': self.cover_image_url
        }

# Helper function to get a random book from the database filtered by genre
def get_random_book(genre=None):
    if genre:
        books = Book.query.filter(Book.genre.ilike(f'%{genre}%')).all()
    else:
        books = Book.query.all()
    
    print(f"Books retrieved for genre '{genre}': {books}")  # Debug log

    return random.choice(books) if books else None

# Endpoint to get a random book
@bookrec_api.route('/random_bookrec', methods=['GET'])
def random_bookrec():
    genre = request.args.get('genre')  # Get the 'genre' parameter from the request
    print(f"Received genre: {genre}")  # Debug log
    
    while True:
        book = get_random_book(genre)
        if book:
            return jsonify(book.to_dict())
        else:
            print("No books found, retrying in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    # Register the Blueprint with the app
    app.register_blueprint(bookrec_api)

    # Only create tables if they do not exist
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5003)