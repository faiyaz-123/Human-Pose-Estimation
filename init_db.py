import sqlite3
import os
from hashlib import sha256

def initialize_database():
    """Initialize the SQLite database with proper tables and security."""
    # Use absolute path for reliability across environments
    db_path = os.path.join(os.path.dirname(__file__), "users.db")
    
    try:
        # Establish database connection
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Create users table with enhanced security
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        ''')

        # Create sessions table for enhanced functionality
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')

        # Insert default admin user with hashed credentials
        salt = os.urandom(16).hex()
        default_password = "admin@123"  # CHANGE THIS IN PRODUCTION
        hashed_password = sha256((default_password + salt).encode()).hexdigest()
        
        cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, salt)
        VALUES (?, ?, ?)
        ''', ('admin', hashed_password, salt))

        connection.commit()
        print(f"✅ Database initialized successfully at {db_path}")

    except sqlite3.Error as error:
        print(f"❌ Database error: {error}")
    finally:
        if connection:
            connection.close()

def get_db_connection():
    """Establish and return a database connection."""
    db_path = os.path.join(os.path.dirname(__file__), "users.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable dictionary-style access
    return conn

if __name__ == "__main__":
    initialize_database()