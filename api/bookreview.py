from flask import Blueprint, jsonify
from flask_cors import CORS
from flask_restful import Api
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import random
from model.librarydb import books  

bookreview_api = Blueprint('bookreview_api', __name__, url_prefix='/api')
api = Api(bookreview_api)

CORS(bookreview_api)

engine = create_engine('sqlite:///library.db', echo=True) 
Session = sessionmaker(bind=engine)
session = Session()

# Function to get a random book
def get_random_book():
    books_query = session.query(books).all()  
    return random.choice(books_query) if books_query else None

@bookreview_api.route('/random_book', methods=['GET'])  
def random_book():
    book = get_random_book()
    if book:
        return jsonify({
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'description': book.description,
            'image_cover': book.cover_image_url
        })
    else:
        return jsonify({'error': 'No books found'}), 404
