from flask import Blueprint, jsonify, request
from flask_restful import Api
from model.librarydb import Book
from model.commentsdb import Comments
from model.user import User
import random
from __init__ import app, db

bookreview_api = Blueprint('bookreview_api', __name__, url_prefix='/api')
api = Api(bookreview_api)

# Fetch Random Book
def get_random_book():
    try:
        books_query = Book.query.all()
        if books_query:
            return random.choice(books_query)
        else:
            return None
    except Exception as e:
        print(f"Error while fetching random book: {e}")
        return None

# Fetch Comments for a Book
def get_comments_for_book(book_id=None):
    if book_id:
        comments_query = Comments.query.filter_by(book_id=book_id).all()
    else:
        comments_query = Comments.query.all()

    return [{
        "id": comment.id,
        "book_id": comment.book_id,
        "user_id": comment.user_id,
        "comment_text": comment.comment_text
    } for comment in comments_query]

# Route to fetch a random book
@bookreview_api.route('/random_book', methods=['GET'])
def random_book():
    book = get_random_book()
    if book:
        comments = get_comments_for_book(book_id=book.id)
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'description': book.description,
            'cover_url': book.cover_url,
            'comments': comments
        })
    else:
        return jsonify({'error': 'No books found'}), 404

# Route to fetch a book by ID (this should handle /bookrates/{book_id} style URLs)
@bookreview_api.route('/books/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    comments = get_comments_for_book(book_id=book.id)
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'genre': book.genre,
        'description': book.description,
        'cover_url': book.cover_url,
        'comments': comments
    })

# Comments Route (GET, POST, PUT, DELETE)
@bookreview_api.route('/comments', methods=['GET', 'POST'])
def manage_comments():
    if request.method == 'GET':
        book_id = request.args.get('book_id')

        if not book_id:
            return jsonify({'error': 'Book ID is required'}), 400

        comments = get_comments_for_book(book_id)
        if comments:
            return jsonify({'comments': comments})
        else:
            return jsonify({'message': 'No comments found for this book'}), 404

    elif request.method == 'POST':
        try:
            data = request.get_json()

            book_id = data.get('book_id')
            user_id = data.get('user_id')
            comment_text = data.get('comment_text')

            if not book_id or not user_id or not comment_text:
                return jsonify({'error': 'Missing required fields: book_id, user_id, or comment_text'}), 400

            book = Book.query.get(book_id)
            if not book:
                return jsonify({'error': 'Book not found'}), 404

            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404

            new_comment = Comments(
                book_id=book_id,
                user_id=user.id,
                comment_text=comment_text
            )

            db.session.add(new_comment)
            db.session.commit()

            return jsonify({
                'id': new_comment.id,
                'book_id': new_comment.book_id,
                'user_id': new_comment.user_id,
                'comment_text': new_comment.comment_text
            }), 201

        except Exception as e:
            print(f"Error while adding comment: {e}")
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error'}), 500

# PUT and DELETE for Comments (Route: /api/comments/<comment_id>)
@bookreview_api.route('/comments/<int:comment_id>', methods=['PUT', 'DELETE'])
def update_delete_comment(comment_id):
    comment = Comments.query.get(comment_id)

    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    if request.method == 'PUT':
        try:
            data = request.get_json()
            comment_text = data.get('comment_text')

            if not comment_text:
                return jsonify({'error': 'Comment text is required'}), 400

            comment.comment_text = comment_text
            db.session.commit()

            return jsonify({
                'id': comment.id,
                'book_id': comment.book_id,
                'user_id': comment.user_id,
                'comment_text': comment.comment_text
            })

        except Exception as e:
            print(f"Error while updating comment: {e}")
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error'}), 500

    elif request.method == 'DELETE':
        try:
            db.session.delete(comment)
            db.session.commit()
            return jsonify({'message': 'Comment deleted successfully'}), 200
        except Exception as e:
            print(f"Error while deleting comment: {e}")
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error'}), 500


# POST, PUT, DELETE for Book (Route: /api/books)
@bookreview_api.route('/books', methods=['POST'])
def create_book():
    try:
        data = request.get_json()

        title = data.get('title')
        author = data.get('author')
        genre = data.get('genre')
        description = data.get('description')
        cover_url = data.get('cover_url')

        if not title or not author:
            return jsonify({'error': 'Title and author are required'}), 400

        new_book = Book(
            title=title,
            author=author,
            genre=genre,
            description=description,
            cover_url=cover_url
        )

        db.session.add(new_book)
        db.session.commit()

        return jsonify({
            'id': new_book.id,
            'title': new_book.title,
            'author': new_book.author,
            'genre': new_book.genre,
            'description': new_book.description,
            'cover_url': new_book.cover_url
        }), 201

    except Exception as e:
        print(f"Error while creating book: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error'}), 500


# PUT and DELETE for Book (Route: /api/books/<book_id>)
@bookreview_api.route('/books/<int:book_id>', methods=['PUT', 'DELETE'])
def update_delete_book(book_id):
    book = Book.query.get(book_id)

    # Check if the book exists
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    if request.method == 'PUT':
        try:
            data = request.get_json()
            book.title = data.get('title', book.title)
            book.author = data.get('author', book.author)
            book.genre = data.get('genre', book.genre)
            book.description = data.get('description', book.description)
            book.cover_url = data.get('cover_url', book.cover_url)
            db.session.commit()

            return jsonify({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'genre': book.genre,
                'description': book.description,
                'cover_url': book.cover_url
            })

        except Exception as e:
            print(f"Error while updating book: {e}")
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error'}), 500

    elif request.method == 'DELETE':
        try:
            # Log the book ID to ensure correct value
            print(f"Attempting to delete book with ID: {book_id}")

            # Deleting the book
            db.session.delete(book)
            db.session.commit()

            return jsonify({'message': 'Book deleted successfully'}), 200

        except Exception as e:
            print(f"Error while deleting book: {e}")
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error'}), 500