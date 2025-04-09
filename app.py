import streamlit as st
import cv2
import mediapipe as mp
import math
import time
import sqlite3
import os

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Custom Page Configuration
def set_page_config():
    st.set_page_config(
        page_title="Human Pose Estimation",
        page_icon="💪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Enhanced CSS with dark title bars
    st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
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
        .stTextInput>div>div>input {
            border-radius: 8px;
            padding: 8px;
        }
        .stSelectbox>div>div>select {
            border-radius: 8px;
            padding: 8px;
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

# Function to calculate angle between three points
def calculate_angle(a, b, c):
    ang = math.degrees(math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x))
    return ang + 360 if ang < 0 else ang

# Database Functions
def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def authenticate_user(username, password):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if user and user["password"] == password:
        return True
    return False

def register_user(username, password):
    conn = get_db_connection()
    existing_user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if existing_user:
        conn.close()
        return False
    conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return True

def users_exist():
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return len(users) > 0

# Enhanced UI Pages with Dark Titles
def login_page():
    st.markdown('<div class="dark-title"><h1>Welcome to Human Pose Estimation 🏋️</h1></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://deeplobe.ai/wp-content/uploads/2023/04/Deeplobe-Pose-Detection-Yoga-Image-1024x683.png", 
                      width=400)
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
    st.markdown('<div class="dark-title"><h1>Create Your Account 🏆</h1></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=500", 
                    width=400)
        with col2:
            st.markdown('<div class="exercise-title"><h3>Account Registration</h3></div>', unsafe_allow_html=True)
            username = st.text_input("👤 Choose a username")
            password = st.text_input("🔒 Choose a password", type="password")
            
            if st.button("Register", key="register_btn"):
                if register_user(username, password):
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
    st.markdown(f'<div class="dark-title"><h1>Hello, {st.session_state.username}! 👋</h1></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Exercise Selection Card
    with st.container():
        st.markdown('<div class="exercise-title"><h3>🏃 Choose Your Exercise</h3></div>', unsafe_allow_html=True)
        exercise = st.selectbox("", ["Squats", "Hand Raises", "Yoga - Tree Pose", "Yoga - Warrior II"])
        st.markdown(f"<div class='exercise-card'>"
                   f"<h4>Current Exercise: {exercise}</h4>"
                   f"<p>Follow the on-screen guidance</p></div>", 
                   unsafe_allow_html=True)
    
    # Initialize counters and stages
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
    
    # Webcam Feed
    if st.session_state.webcam_active:
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
            
            try:
                landmarks = results.pose_landmarks.landmark
                
                # Get coordinates for key points
                shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
                ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
                wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
                elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]

                # Exercise-specific logic
                if exercise == "Squats":
                    knee_angle = calculate_angle(hip, knee, ankle)
                    if knee_angle > 160:
                        st.session_state.squat_stage = "up"
                    if knee_angle < 90 and st.session_state.squat_stage == "up":
                        st.session_state.squat_stage = "down"
                        st.session_state.counter += 1
                    if knee_angle < 90:
                        cv2.putText(image, "Lower!", (image.shape[1] - 200, 50), 
                                   cv2.FONT_HERSHEY_TRIPLEX, 0.9, (0, 0, 255), 2)
                    elif knee_angle > 160:
                        cv2.putText(image, "Good!", (image.shape[1] - 200, 50), 
                                   cv2.FONT_HERSHEY_TRIPLEX, 0.9, (0, 255, 0), 2)

                elif exercise == "Hand Raises":
                    if wrist.y < shoulder.y:
                        if st.session_state.handraise_stage != "up":
                            st.session_state.handraise_stage = "up"
                            st.session_state.counter += 1
                    else:
                        st.session_state.handraise_stage = "down"
                    if wrist.y < shoulder.y:
                        cv2.putText(image, "Raised!", (image.shape[1] - 200, 100), 
                                   cv2.FONT_HERSHEY_TRIPLEX, 0.9, (0, 255, 0), 2)
                    else:
                        cv2.putText(image, "Lower Hands!", (image.shape[1] - 200, 100), 
                                   cv2.FONT_HERSHEY_TRIPLEX, 0.9, (0, 0, 255), 2)

                elif exercise == "Yoga - Tree Pose":
                    raised_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
                    standing_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
                    standing_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

                    if (raised_ankle.y > standing_knee.y and 
                        abs(raised_ankle.x - standing_hip.x) < 0.1):
                        cv2.putText(image, "Good Pose!", (image.shape[1] - 200, 50), 
                                   cv2.FONT_HERSHEY_TRIPLEX, 0.9, (0, 255, 0), 2)
                        if 'tree_pose_start_time' not in st.session_state:
                            st.session_state.tree_pose_start_time = time.time()
                        if time.time() - st.session_state.tree_pose_start_time >= 2:
                            st.session_state.counter += 1
                            st.session_state.tree_pose_start_time = None
                    else:
                        cv2.putText(image, "Adjust Pose!", (image.shape[1] - 200, 50), 
                                   cv2.FONT_HERSHEY_TRIPLEX, 0.9, (0, 0, 255), 2)
                        st.session_state.tree_pose_start_time = None

                elif exercise == "Yoga - Warrior II":
                    front_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
                    front_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
                    knee_angle = calculate_angle(hip, front_knee, front_ankle)

                    if 80 < knee_angle < 100:
                        cv2.putText(image, "Good Pose!", (image.shape[1] - 200, 50), 
                                   cv2.FONT_HERSHEY_TRIPLEX, 0.9, (0, 255, 0), 2)
                        if 'warrior_pose_start_time' not in st.session_state:
                            st.session_state.warrior_pose_start_time = time.time()
                        if time.time() - st.session_state.warrior_pose_start_time >= 2:
                            st.session_state.counter += 1
                            st.session_state.warrior_pose_start_time = None
                    else:
                        cv2.putText(image, "Adjust Pose!", (image.shape[1] - 200, 50), 
                                   cv2.FONT_HERSHEY_TRIPLEX, 0.9, (0, 0, 255), 2)
                        st.session_state.warrior_pose_start_time = None

            except Exception as e:
                pass

            # Draw pose landmarks
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Display counter on frame
            cv2.putText(image, f"Reps: {st.session_state.counter}", (10, 30), 
                       cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 0, 0), 2)

            # Show frame
            video_placeholder.image(image, channels="BGR")

            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

# Main App Logic
def main():
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