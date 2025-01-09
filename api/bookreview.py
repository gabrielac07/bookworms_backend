from flask import Blueprint, jsonify
from flask_cors import CORS
from flask_restful import Api
import sqlite3
import random

bookreview_api = Blueprint('bookreview_api', __name__, url_prefix='/api')
api = Api(bookreview_api)

CORS(bookreview_api)

def get_random_book():
    conn = sqlite3.connect('books.db')  
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()
    return random.choice(books) if books else None

@bookreview_api.route('/random_book', methods=['GET'])  
def random_book():
    book = get_random_book()
    if book:
        return jsonify({
            'title': book[1],
            'author': book[2],
            'genre': book[3],
            'description': book[4],
            'image_cover': book[5]
        })
    else:
        return jsonify({'error': 'No books found'}), 404
