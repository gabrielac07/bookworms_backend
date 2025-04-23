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
@bookrec_api.route("/bookrec", methods=['POST']) # This is the endpoint to add a book to the savebookrec table
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
 
# Read and display all book recommendations
@bookrec_api.route("/bookrec/book", methods=['GET'])
def get_books():
    try:
        # Query all add books recs
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

# Endpoint to update a book recommendation
@bookrec_api.route('/bookrec', methods=['PUT']) 
def update_book():
    data = request.json # Get the data from the request
    title = data.get('title')

    if not title:
        return jsonify({'error': 'Title is required to update the book'}), 400

    book = SaveBookRec.query.filter_by(title=title).first()
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    try:
        book.author = data.get('author', book.author)
        book.genre = data.get('genre', book.genre)
        book.description = data.get('description', book.description)
        book.cover_url = data.get('cover_url', book.cover_url)
        db.session.commit()
        return jsonify({'message': 'Book updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update book', 'message': str(e)}), 500

# Endpoint to delete a book recommendation
@bookrec_api.route('/bookrec', methods=['DELETE'])
def delete_book():
    data = request.json
    
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title is required to delete the book'}), 400

    try:
        bookrec = SaveBookRec.query.filter_by(title=title).first()
        
        if not bookrec:
            return jsonify({'error': 'Book not found'}), 404
        
        db.session.delete(bookrec)
        db.session.commit()
        
        return jsonify({'message': 'Book deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to delete book', 'message': str(e)}), 500

