from flask import Blueprint, jsonify, request
import sqlite3

# Create a Blueprint for the suggestion functionality
suggest_api = Blueprint('suggest_api', __name__, url_prefix='/api/suggest')

DATABASE = 'suggestions.db'  # Database containing the books table

def get_db_connection(database):
    """Establish a database connection to the specified database."""
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    """Initialize the database by creating the books table."""
    conn = get_db_connection(DATABASE)

    # Drop the books table if it exists to ensure no conflicts with schema changes
    conn.execute('DROP TABLE IF EXISTS books')
    conn.commit()

    # Create the books table
    create_books_table = '''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        genre TEXT,
        description TEXT,
        cover_image_url TEXT
    );
    '''
    conn.execute(create_books_table)
    conn.commit()
    conn.close()
    print("Database initialized with the books table!")

# Route to get all books
@suggest_api.route('/books', methods=['GET'])
def get_books():
    """Retrieve all books from the database."""
    conn = get_db_connection(DATABASE)
    books = conn.execute('SELECT id, title, author, genre, description, cover_image_url FROM books').fetchall()
    conn.close()
    return jsonify([dict(book) for book in books])

# Route to add a new book suggestion
@suggest_api.route('/books', methods=['POST'])
def add_book():
    """Add a new book to the database."""
    if request.is_json:
        data = request.get_json()
        title = data.get('title')
        author = data.get('author')
        genre = data.get('genre', '')
        description = data.get('description', '')
        cover_image_url = data.get('cover_image_url', '')

        # Validate that title and author are provided
        if not title or not author:
            return jsonify({"error": "Missing required fields: title or author"}), 400

        conn = get_db_connection(DATABASE)
        conn.execute(
            'INSERT INTO books (title, author, genre, description, cover_image_url) VALUES (?, ?, ?, ?, ?)',
            (title, author, genre, description, cover_image_url)
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Book added successfully"}), 201

    return jsonify({"error": "Request must be JSON"}), 415

# Route to update an existing book
@suggest_api.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update an existing book in the database."""
    if request.is_json:
        data = request.get_json()
        title = data.get('title')
        author = data.get('author')
        genre = data.get('genre')
        description = data.get('description')
        cover_image_url = data.get('cover_image_url')

        conn = get_db_connection(DATABASE)
        conn.execute(
            '''
            UPDATE books
            SET title = ?, author = ?, genre = ?, description = ?, cover_image_url = ?
            WHERE id = ?
            ''',
            (title, author, genre, description, cover_image_url, book_id)
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Book updated successfully"}), 200

    return jsonify({"error": "Request must be JSON"}), 415

# Route to delete a book
@suggest_api.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book from the database."""
    conn = get_db_connection(DATABASE)
    conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Book deleted successfully"}), 200

# Initialize the database when this module is imported
init_db()