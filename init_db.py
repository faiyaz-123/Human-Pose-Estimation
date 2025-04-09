<<<<<<< HEAD
import sqlite3

def initialize_db():
    """
    Initialize the SQLite database and create the users table.
    """
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create a table to store user credentials
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    # Insert a sample user (for testing)
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)
    ''', ('admin', 'password'))  # In a real app, hash the password!

    # Commit changes and close the connection
    conn.commit()

    # Verify the table and data
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    print("Users in the database:", users)

    conn.close()

if __name__ == "__main__":
=======
import sqlite3

def initialize_db():
    """
    Initialize the SQLite database and create the users table.
    """
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create a table to store user credentials
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    # Insert a sample user (for testing)
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)
    ''', ('admin', 'password'))  # In a real app, hash the password!

    # Commit changes and close the connection
    conn.commit()

    # Verify the table and data
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    print("Users in the database:", users)

    conn.close()

if __name__ == "__main__":
>>>>>>> e8f628ac6b92ca3977e14fe94bfd4b4080450892
    initialize_db()