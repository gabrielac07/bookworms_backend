from flask import Blueprint, jsonify, request
import sqlite3

# Create a Blueprint for the wish list functionality
wishlist_api = Blueprint('wishlist_api', __name__, url_prefix='/api/wishlist')

DATABASE = 'books.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This will allow us to access columns by name
    return conn

def init_db():
    """Initialize the database by creating necessary tables."""
    conn = get_db_connection()
    # SQL command to create the wishlist table
    create_wishlist_table = '''
    CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        FOREIGN KEY (book_id) REFERENCES books (id)
    );
    '''
    conn.execute(create_wishlist_table)
    conn.commit()
    conn.close()
    print("Database initialized with wishlist table!")

# Route to get a user's wish list
@wishlist_api.route('/<int:user_id>', methods=['GET'])
def get_wishlist(user_id):
    conn = get_db_connection()
    # Fetch all books in the user's wish list by joining books and wishlist tables
    books = conn.execute(
        '''
        SELECT books.id, books.title, books.author
        FROM wishlist
        JOIN books ON wishlist.book_id = books.id
        WHERE wishlist.user_id = ?
        ''',
        (user_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(book) for book in books])

# Route to add an existing book to the user's wish list
@wishlist_api.route('/', methods=['POST'])
def add_book_to_wishlist():
    if request.is_json:  # Check if the content is JSON
        data = request.get_json()  # Parse JSON data
        user_id = data.get('user_id')  # Retrieve user ID
        book_id = data.get('book_id')  # Retrieve book ID

        # Validate that both user_id and book_id are provided
        if not user_id or not book_id:
            return jsonify({"error": "Missing user_id or book_id"}), 400

        conn = get_db_connection()

        # Check if the book exists in the books table
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        if not book:
            conn.close()
            return jsonify({"error": "Book not found"}), 404

        # Check if the book is already in the user's wish list
        existing_entry = conn.execute(
            'SELECT * FROM wishlist WHERE user_id = ? AND book_id = ?',
            (user_id, book_id)
        ).fetchone()
        if existing_entry:
            conn.close()
            return jsonify({"message": "Book already in wish list"}), 200

        # Add the book to the user's wish list
        conn.execute('INSERT INTO wishlist (user_id, book_id) VALUES (?, ?)', (user_id, book_id))
        conn.commit()
        conn.close()

        return jsonify({"message": "Book added to user's wish list"}), 201

    else:
        return jsonify({"error": "Request must be JSON"}), 415

# Initialize the database when this module is imported
init_db()
