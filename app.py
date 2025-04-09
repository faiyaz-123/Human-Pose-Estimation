import streamlit as st
import cv2
import mediapipe as mp
import math
import time
import sqlite3
import os
from hashlib import sha256
from datetime import datetime

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Database Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def initialize_database():
    """Initialize the database with secure tables"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
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
        
        # Create sessions table for enhanced security
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')
        
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database initialization error: {e}")
    finally:
        if conn:
            conn.close()

def get_db_connection():
    """Get a secure database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password, salt=None):
    """Hash password with salt using SHA-256"""
    salt = salt or os.urandom(16).hex()
    return sha256((password + salt).encode()).hexdigest(), salt

# Custom Page Configuration
def set_page_config():
    st.set_page_config(
        page_title="Human Pose Estimation",
        page_icon="💪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Enhanced CSS with dark theme
    st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        .dark-title {
            background-color: #2c3e50;
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .exercise-title {
            background-color: #34495e;
            color: white;
            padding: 12px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            border: none;
            font-weight: bold;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #45a049;
            transform: scale(1.02);
        }
        .exercise-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .counter-display {
            font-size: 2rem;
            font-weight: bold;
            color: #4CAF50;
            text-align: center;
            margin: 20px 0;
            padding: 10px;
            background: #e8f5e9;
            border-radius: 10px;
        }
        .webcam-container {
            border: 2px solid #4CAF50;
            border-radius: 10px;
            padding: 10px;
            margin-top: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

# Pose Calculation Functions
def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    ang = math.degrees(math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x))
    return ang + 360 if ang < 0 else ang

# Authentication Functions
def authenticate_user(username, password):
    """Secure user authentication with hashed passwords"""
    try:
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", 
            (username,)
        ).fetchone()
        
        if user:
            # Verify password hash
            input_hash = sha256((password + user['salt']).encode()).hexdigest()
            if input_hash == user['password_hash']:
                # Update last login
                conn.execute(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (datetime.now(), user['id'])
                )
                conn.commit()
                return True
        return False
    except sqlite3.Error as e:
        st.error(f"Authentication error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def register_user(username, password):
    """Secure user registration with password hashing"""
    try:
        conn = get_db_connection()
        
        # Check if username exists
        if conn.execute(
            "SELECT 1 FROM users WHERE username = ?", 
            (username,)
        ).fetchone():
            return False
            
        # Hash password with new salt
        password_hash, salt = hash_password(password)
        
        conn.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, password_hash, salt)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Registration error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def users_exist():
    """Check if any users exist in database"""
    try:
        conn = get_db_connection()
        return conn.execute("SELECT 1 FROM users").fetchone() is not None
    except sqlite3.Error:
        return False
    finally:
        if conn:
            conn.close()

# Page Components
def login_page():
    """Login page with secure authentication"""
    st.markdown('<div class="dark-title"><h1>Welcome to Human Pose Estimation 🏋️</h1></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://deeplobe.ai/wp-content/uploads/2023/04/Deeplobe-Pose-Detection-Yoga-Image-1024x683.png", 
                    width=300)
        with col2:
            st.markdown('<div class="exercise-title"><h3>Login to Your Account</h3></div>', unsafe_allow_html=True)
            username = st.text_input("👤 Username")
            password = st.text_input("🔒 Password", type="password")
            
            if st.button("Login", key="login_btn"):
                if authenticate_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
            
            st.markdown("---")
            st.markdown("Don't have an account?")
            if st.button("Register Now", key="go_to_register"):
                st.session_state.register_mode = True
                st.rerun()

def register_page():
    """Secure user registration page"""
    st.markdown('<div class="dark-title"><h1>Create Your Account 🏆</h1></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=500", 
                    width=300)
        with col2:
            st.markdown('<div class="exercise-title"><h3>Account Registration</h3></div>', unsafe_allow_html=True)
            username = st.text_input("👤 Choose a username")
            password = st.text_input("🔒 Choose a password", type="password")
            confirm_password = st.text_input("🔒 Confirm password", type="password")
            
            if st.button("Register", key="register_btn"):
                if password != confirm_password:
                    st.error("Passwords don't match!")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters")
                elif register_user(username, password):
                    st.success("Account created! Please login.")
                    st.session_state.register_mode = False
                    st.rerun()
                else:
                    st.error("Username already exists")
            
            st.markdown("---")
            st.markdown("Already have an account?")
            if st.button("Back to Login", key="go_to_login"):
                st.session_state.register_mode = False
                st.rerun()

def pose_estimation_page():
    """Main pose estimation interface"""
    st.markdown(f'<div class="dark-title"><h1>Hello, {st.session_state.username}! 👋</h1></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Exercise Selection
    with st.container():
        st.markdown('<div class="exercise-title"><h3>🏃 Choose Your Exercise</h3></div>', unsafe_allow_html=True)
        exercise = st.selectbox("", ["Squats", "Hand Raises", "Yoga - Tree Pose", "Yoga - Warrior II"])
        st.markdown(f"<div class='exercise-card'>"
                   f"<h4>Current Exercise: {exercise}</h4>"
                   f"<p>Follow the on-screen guidance</p></div>", 
                   unsafe_allow_html=True)
    
    # Initialize session variables
    if 'counter' not in st.session_state:
        st.session_state.counter = 0
    if 'webcam_active' not in st.session_state:
        st.session_state.webcam_active = False
    if 'squat_stage' not in st.session_state:
        st.session_state.squat_stage = "up"
    if 'handraise_stage' not in st.session_state:
        st.session_state.handraise_stage = "down"
    
    # Counter Display
    st.markdown(f"<div class='counter-display'>"
               f"Rep Count: {st.session_state.counter}"
               f"</div>", unsafe_allow_html=True)
    
    # Control Buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎥 Start Webcam" if not st.session_state.webcam_active else "🛑 Stop Webcam"):
            st.session_state.webcam_active = not st.session_state.webcam_active
    with col2:
        if st.button("🔁 Reset Counter"):
            st.session_state.counter = 0
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.success("Logged out successfully!")
            st.rerun()
    
    # Webcam Processing
    if st.session_state.webcam_active:
        process_webcam_feed(exercise)

def process_webcam_feed(exercise):
    """Process real-time webcam feed for pose estimation"""
    st.markdown("---")
    st.markdown('<div class="exercise-title"><h3>🎥 Live Pose Detection</h3></div>', unsafe_allow_html=True)
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    video_placeholder = st.empty()
    
    while st.session_state.webcam_active:
        ret, frame = cap.read()
        if not ret:
            st.error("Camera error")
            break
        
        # Process frame with MediaPipe
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        if results.pose_landmarks:
            process_pose_landmarks(results.pose_landmarks, exercise, image)
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        # Display counter on frame
        cv2.putText(image, f"Reps: {st.session_state.counter}", (10, 30), 
                   cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 0, 0), 2)
        
        # Show frame
        video_placeholder.image(image, channels="BGR")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def process_pose_landmarks(landmarks, exercise, image):
    """Process pose landmarks for specific exercises"""
    try:
        # Get key points
        shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE.value]
        ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value]
        
        if exercise == "Squats":
            knee_angle = calculate_angle(hip, knee, ankle)
            if knee_angle > 160:
                st.session_state.squat_stage = "up"
            if knee_angle < 90 and st.session_state.squat_stage == "up":
                st.session_state.squat_stage = "down"
                st.session_state.counter += 1
            
            feedback = "Lower!" if knee_angle < 90 else "Good!" if knee_angle > 160 else ""
            cv2.putText(image, feedback, (image.shape[1] - 200, 50), 
                       cv2.FONT_HERSHEY_TRIPLEX, 0.9, (0, 0, 255) if knee_angle < 90 else (0, 255, 0), 2)

        elif exercise == "Hand Raises":
            if wrist.y < shoulder.y:
                if st.session_state.handraise_stage != "up":
                    st.session_state.handraise_stage = "up"
                    st.session_state.counter += 1
            else:
                st.session_state.handraise_stage = "down"
            
            feedback = "Raised!" if wrist.y < shoulder.y else "Lower Hands!"
            cv2.putText(image, feedback, (image.shape[1] - 200, 100), 
                       cv2.FONT_HERSHEY_TRIPLEX, 0.9, (0, 255, 0) if wrist.y < shoulder.y else (0, 0, 255), 2)

    except Exception as e:
        st.error(f"Pose processing error: {e}")

# Main Application
def main():
    # Initialize database if needed
    if not os.path.exists(DB_PATH):
        initialize_database()
    
    set_page_config()
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'register_mode' not in st.session_state:
        st.session_state.register_mode = False
    
    # Page routing
    if not st.session_state.logged_in:
        if st.session_state.register_mode or not users_exist():
            register_page()
        else:
            login_page()
    else:
        pose_estimation_page()

if __name__ == "__main__":
    main()