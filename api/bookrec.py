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
                'image_cover': book.cover_url
            })
        else: # Retry if no books are found in the database for the requested genre
            return jsonify({"error": "No books found, retrying in 5 seconds..."}), 404
            time.sleep(5)
            #print("No books found, retrying in 5 seconds...")

# Endpoint to save a book recommendation (This is what I'm using for the table checkpoint on Thurs/Fri)
@bookrec_api.route("/add_bookrec", methods=['POST']) # This is the endpoint to add a book to the savebookrec table
def add_book():
    data = request.get_json() # Get the data from the request
    title = data.get('title') 
    author = data.get('author')
    genre = data.get('genre')
    description = data.get('description')
    cover_url = data.get('cover_url') 

    if not title or not author:
        return jsonify({"error": "Title and author are required"}), 400

    new_book = SaveBookRec( # Create a new book object
        title=title,
        author=author,
        genre=genre,
        description=description,
        cover_url=cover_url
    )

    db.session.add(new_book) # Add the new book to the savebookrec table
    db.session.commit() # Commit the changes to the database
    
    return jsonify({"message": "Book added successfully", 'success': True, 'id': new_book.id}), 201

# Read a single book recommendation by ID
@bookrec_api.route("/get_bookrec/<int:id>", methods=['GET']) # after the get_bookrec/ enter the id number (USE 1 or 2) of the book you want to get
def get_single_book(id):
    book = SaveBookRec.query.get(id)

    if not book:
        return jsonify({"error": "Book not found"}), 404

    return jsonify(book.read()), 200 

# Read and display all book recommendations
@bookrec_api.route("/get_bookrecs", methods=['GET'])
def get_book():
    try:
        # Query all suggested books
        books = SaveBookRec.query.all()

        # Convert the list of book objects to a list of dictionaries
        books_data = [
            {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'genre': book.genre,
                'description': book.description,
                'cover_url': book.cover_url
            }
            for book in books
        ]

        return jsonify(books_data), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch books', 'message': str(e)}), 500

# Update an existing book recommendation by id number assigned to it on the table
@bookrec_api.route("/update_bookrec/<int:id>", methods=['PUT']) # after the update_bookrec/ enter the id number (USE 3 and change the genre to Fantasy) of the book you want to update
def update_book(id):
    data = request.json # Get the data from the request

    try:
        book = SaveBookRec.query.get(id) # Get the book by ID from the savebookrec table

        if not book:
            return jsonify({"error": "Book not found"}), 404
    #update book titles
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.genre = data.get('genre', book.genre)
        book.description = data.get('description', book.description)
        book.cover_url = data.get('cover_url', book.cover_url)
    
        db.session.commit() # Commit the changes to the database
    
        return jsonify({"message": "Book updated successfully"}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update book', 'message': str(e)}), 500

# Delete an existing book recommendation by id number assigned to it on the table
@bookrec_api.route("/delete_bookrec/<int:id>", methods=['DELETE']) # after the delete_bookrec/ enter the id number (USE 3) to deleted the added book (A Feast for Crows)
def delete_book(id):
    book = SaveBookRec.query.get(id) # Get the book by ID from the savebookrec table

    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(book) # Delete the book from the savebookrec table
    db.session.commit() # Commit the changes to the database
    
    return jsonify({"message": "Book deleted successfully"}), 200