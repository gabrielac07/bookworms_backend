from flask import Blueprint, jsonify, request
import sqlite3

# Create a Blueprint for the wishlist functionality
wishlist_api = Blueprint('wishlist_api', __name__, url_prefix='/api/wishlist')

DATABASE = 'books.db'  # Existing database containing the books table

def get_db_connection(database):
    """Establish a database connection to the specified database."""
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row  # Access columns by name
    conn.execute('PRAGMA foreign_keys = ON')  # Enable foreign key constraints
    return conn

def init_db():
    """Initialize the database by creating the wishlist table."""
    conn = get_db_connection(DATABASE)

    # Drop the wishlist table if it exists to ensure no conflicts with schema changes
    conn.execute('DROP TABLE IF EXISTS wishlist')
    conn.commit()

    # Create the wishlist table without the user_uid (no user_id)
    create_wishlist_table = '''
    CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,  -- Reference to books table
        FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE
    );
    '''
    conn.execute(create_wishlist_table)
    conn.commit()
    conn.close()
    print("Database initialized with the wishlist table!")

# Route to get a dropdown list of books
@wishlist_api.route('/books', methods=['GET'])
def get_books():
    """Retrieve all books from the database to display in a dropdown menu."""
    conn = get_db_connection(DATABASE)
    books = conn.execute('SELECT id, title, author FROM books').fetchall()
    conn.close()
    return jsonify([dict(book) for book in books])

# Route to get all books in the wishlist (no user associated)
@wishlist_api.route('/', methods=['GET'])
def get_wishlist():
    """Retrieve all books in the wishlist."""
    conn = get_db_connection(DATABASE)
    books = conn.execute(
        '''
        SELECT books.id, books.title, books.author
        FROM wishlist
        JOIN books ON wishlist.book_id = books.id
        '''
    ).fetchall()
    conn.close()
    return jsonify([dict(book) for book in books])

# Route to add a book to the wishlist
@wishlist_api.route('/', methods=['POST'])
def add_book_to_wishlist():
    """Add a book to the wishlist."""
    if request.is_json:
        data = request.get_json()
        book_id = data.get('book_id')

        # Validate that book_id is provided
        if not book_id:
            return jsonify({"error": "Missing book_id"}), 400

        # Check if the book exists in the books database
        conn = get_db_connection(DATABASE)
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        if not book:
            conn.close()
            return jsonify({"error": "Book not found"}), 404

        # Check if the book is already in the wishlist
        existing_entry = conn.execute(
            'SELECT * FROM wishlist WHERE book_id = ?',
            (book_id,)
        ).fetchone()
        if existing_entry:
            conn.close()
            return jsonify({"message": "Book already in wishlist"}), 200

        # Add the book to the wishlist
        conn.execute(
            'INSERT INTO wishlist (book_id) VALUES (?)',
            (book_id,)
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Book added to wishlist"}), 201

    return jsonify({"error": "Request must be JSON"}), 415

# Initialize the database when this module is imported
init_db()
