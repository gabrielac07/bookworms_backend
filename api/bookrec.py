from flask import Flask, jsonify
from flask_cors import CORS  # Import CORS
import sqlite3
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Helper function to get a random book from the database
def get_random_book():
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()

    # Pick a random book
    return random.choice(books) if books else None

# Endpoint to get a random book
@app.route('/api/random_book', methods=['GET'])
def random_book():
    book = get_random_book()
    if book:
        return jsonify({
            'title': book[1],
            'author': book[2],
            'description': book[3], # Book description
            'image_cover': book[4]    # Book cover image URL
        })
    else:
        return jsonify({'error': 'No books found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5002)
