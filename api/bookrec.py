from flask import jsonify, request, Blueprint
from flask_restful import Api
from model.librarydb import Book
from model.bookrecdb import SaveBookRec
from __init__ import app, db 
import random
import time

bookrec_api = Blueprint('bookrec_api', __name__, url_prefix='/api')
# API docs https://flask-restful.readthedocs.io/en/latest/ <-- just for reference
api = Api(bookrec_api)

# Helper function to get a random book from the database filtered by genre
def get_random_bookrec(genre=None):
    if genre:
        books = Book.query.filter(Book.genre.ilike(f'%{genre}%')).all() # Fetch a book from the requested genre
    else:
        books = Book.query.all() # Fetch all books if no genre is specified
    
    #print(f"Books retrieved for genre '{genre}': {books}")  # Debug log

    return random.choice(books) if books else None # Return a random book if available

# Endpoint to get a random book
@bookrec_api.route('/random_bookrec', methods=['GET'])
def random_bookrec():
    genre = request.args.get('genre')  # Get the 'genre' parameter from the request 
    #print(f"Received genre: {genre}")  # Debug log
    
    while True: # Loop until a book is found 
        book = get_random_bookrec(genre)
        if book:
            return jsonify({
                'title': book.title,
                'author': book.author,
                'description': book.description,
                'image_cover': book.cover_image_url
            })
        else: # Retry if no books are found in the database for the requested genre
            return jsonify({"error": "No books found, retrying in 5 seconds..."}), 404
            time.sleep(5)
            #print("No books found, retrying in 5 seconds...")

# Endpoint to save a book recommendation (This is what I'm using for the table checkpoint on Thurs/Fri)
@bookrec_api.route("/add_bookrec", methods=['POST'])
def add_book():
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    genre = data.get('genre')
    description = data.get('description')
    cover_image_url = data.get('cover_image_url')

    if not title or not author:
        return jsonify({"error": "Title and author are required"}), 400

    new_book = SaveBookRec(
        title=title,
        author=author,
        genre=genre,
        description=description,
        cover_image_url=cover_image_url
    )

    db.session.add(new_book)
    db.session.commit()
    
    return jsonify({"message": "Book added successfully"}), 201

# Read a single book recommendation by ID
@bookrec_api.route("/get_bookrec/<int:id>", methods=['GET'])
def get_book(id):
    book = SaveBookRec.query.get(id)

    if not book:
        return jsonify({"error": "Book not found"}), 404

    return jsonify(book.read()), 200

# Read all book recommendations
@bookrec_api.route("/get_bookrecs", methods=['GET'])
def get_books():
    books = SaveBookRec.query.all()
    return jsonify([book.read() for book in books]), 200

# Update an existing book recommendation by id number assigned to it on the table
@bookrec_api.route("/update_bookrec/<int:id>", methods=['PUT'])
def update_book(id):
    data = request.get_json()
    book = SaveBookRec.query.get(id) # Get the book by ID

    if not book:
        return jsonify({"error": "Book not found"}), 404

    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.genre = data.get('genre', book.genre)
    book.description = data.get('description', book.description)
    book.cover_image_url = data.get('cover_image_url', book.cover_image_url)

    db.session.commit()
    
    return jsonify({"message": "Book updated successfully"}), 200

# Delete an existing book recommendation by id number assigned to it on the table
@bookrec_api.route("/delete_bookrec/<int:id>", methods=['DELETE'])
def delete_book(id):
    book = SaveBookRec.query.get(id)

    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()
    
    return jsonify({"message": "Book deleted successfully"}), 200