from flask import Flask, jsonify, request #Import request to handle query parameters
from flask_cors import CORS  # Import CORS
from flask import Blueprint
from flask_restful import Api, Resource # used for REST API building
import sqlite3
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

bookrec_api = Blueprint('bookrec_api', __name__,
                   url_prefix='/api')

# API docs https://flask-restful.readthedocs.io/en/latest/
api = Api(bookrec_api)

# Helper function to get a random book from the database filtered by genre
def get_random_book(genre=None):
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    #cursor.execute("SELECT * FROM books")
    #books = cursor.fetchall()
    #conn.close()

    if genre:
        #Filter books by genre
        cursor.execute("SELECT * FROM books WHERE LOWER(genre) = ?", (genre.lower(),))
    else:
        #Fetch all books if no genre is provided
        cursor.execute("SELECT * FROM books")
    
    books = cursor.fetchall()
    conn.close()

    #Debug log: Print retrirved book
    print(f"Books retrieved for genre '{genre}': {books}")

    # Pick a random book
    return random.choice(books) if books else None

# Endpoint to get a random book
@app.route('/api/random_book', methods=['GET'])
def random_book():
    genre = request.args.get('genre') # Get the 'genre' parameter from the request
    print(f"Received genre: {genre}")  # Debug log
    
    book = get_random_book(genre)
    if book:
        return jsonify({ # Numbers refer to the books.db column the variable is in (genre is 3 but we don't want to display that when a value is inputted)
            'title': book[1],
            'author': book[2],
            'description': book[4], # Book short summary
            'image_cover': book[5]    # Book cover image URL
        })
    else:
        return jsonify({'error': 'No books found for the specified genre'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
