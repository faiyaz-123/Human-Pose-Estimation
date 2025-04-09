import sqlite3

def authenticate_user(username, password):
    """
    Authenticate a user by checking their credentials in the database.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Fetch the user from the database
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()

    conn.close()

    # Return True if the user exists, otherwise False
    return user is not None

def register_user(username, password):
    """
    Register a new user in the database.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    try:
        # Insert the new user into the database
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # If the username already exists, return False
        return False
    finally:
        conn.close()

def users_exist():
    """
    Check if any users exist in the database.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Fetch all users
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()

    conn.close()

    # Return True if at least one user exists, otherwise False
    return len(users) > 0