from flask import Blueprint, jsonify, request
from flask_restful import Api
from model.librarydb import Book
from model.commentsdb import Comments
from model.user import User
import random
from __init__ import app, db

bookreview_api = Blueprint('bookreview_api', __name__, url_prefix='/api')
api = Api(bookreview_api)

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

@bookreview_api.route('/random_book', methods=['GET'])
def random_book():
    # Handle GET request to fetch random book
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

            user = User.query.get(user_id)  # Assuming user_id is the primary key
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
