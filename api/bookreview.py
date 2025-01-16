from flask import Blueprint, jsonify, request
from flask_restful import Api
from model.librarydb import Book
from model.commentsdb import Comments
import random
from __init__ import app, db

bookreview_api = Blueprint('bookreview_api', __name__, url_prefix='/api')
api = Api(bookreview_api)

def get_random_book():
    try:
        # Query all books
        books_query = Book.query.all()  # Fetch all books from the database
        if books_query:
            return random.choice(books_query)  # Pick a random book if books are available
        else:
            return None  # Returns none if no books are found
    except Exception as e:
        print(f"Error while fetching random book: {e}")
        return None

@bookreview_api.route('/random_book', methods=['GET'])
def random_book():
    book = get_random_book()
    if book:
        # Fetch the comments associated with the book
        comments_query = Comments.query.filter_by(book_id=book.id).all()
        comments = [{"id": comment.id, "username": comment.username, "comment_text": comment.comment_text} for comment in comments_query]

        # If a random book is found, return its details along with comments
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'description': book.description,
            'image_cover': book.cover_image_url,
            'comments': comments  # Include the list of comments
        })
    else:
        # If no book is found, return an error message 
        return jsonify({'error': 'No books found'}), 404

@bookreview_api.route('/comments', methods=['GET', 'POST'])
def manage_comments():
    if request.method == 'GET':
        """
        This handles the GET request to retrieve comments.
        If 'book_id' is provided, it returns comments for that specific book.
        Otherwise, it returns all comments.
        """
        book_id = request.args.get('book_id')

        if book_id:
            # Query comments for the specific book
            comments_query = Comments.query.filter_by(book_id=book_id).all()
            comments = [{"id": comment.id, "username": comment.username, "comment_text": comment.comment_text} for comment in comments_query]
            
            if comments:
                return jsonify({'comments': comments})
            else:
                return jsonify({'message': 'No comments found for this book'}), 404
        else:
            # If no book_id is specified, get all comments
            comments_query = Comments.query.all()
            comments = [{"id": comment.id, "book_id": comment.book_id, "username": comment.username, "comment_text": comment.comment_text} for comment in comments_query]
            
            if comments:
                return jsonify({'comments': comments})
            else:
                return jsonify({'message': 'No comments available'}), 404

    elif request.method == 'POST':
        """
        This handles the POST request to add a new comment.
        It expects a JSON body with book_id, username, and comment_text.
        """
        try:
            # Get the JSON data from the request body
            data = request.get_json()

            # Extract data from the request
            book_id = data.get('book_id')
            username = data.get('username')
            comment_text = data.get('comment_text')

            # Validate the data
            if not book_id or not username or not comment_text:
                return jsonify({'error': 'Missing required fields: book_id, username, or comment_text'}), 400

            # Check if the book exists
            book = Book.query.get(book_id)
            if not book:
                return jsonify({'error': 'Book not found'}), 404

            # Create the new comment
            new_comment = Comments(
                book_id=book_id,
                username=username,
                comment_text=comment_text
            )

            # Add the comment to the session and commit
            db.session.add(new_comment)
            db.session.commit()

            # Return a success response with the created comment details
            return jsonify({
                'id': new_comment.id,
                'book_id': new_comment.book_id,
                'username': new_comment.username,
                'comment_text': new_comment.comment_text
            }), 201

        except Exception as e:
            print(f"Error while adding comment: {e}")
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error'}), 500
