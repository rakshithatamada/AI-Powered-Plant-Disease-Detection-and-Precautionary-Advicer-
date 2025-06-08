import streamlit as st
import numpy as np
import cv2
import sqlite3
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from werkzeug.security import generate_password_hash, check_password_hash

# Database setup
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def register_user(username, email, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    try:
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(email, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    if user and check_password_hash(user[0], password):
        return True
    return False

# Initialize DB
init_db()

# User authentication system
st.title("🌿 Plant Disease Classification 🌿")
st.markdown("<p style='text-align: center; font-size: 19px;'>Helping farmers and plant lovers detect diseases early for healthier crops!</p>", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    menu = ["Home", "Login", "Register"]
    choice = st.selectbox("Select an option", menu)

    if choice == "Register":
        st.subheader("Create an Account")
        new_username = st.text_input("Username")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Register"):
            if new_password == confirm_password:
                if register_user(new_username, new_email, new_password):
                    st.success("Registration successful! You can now log in.")
                else:
                    st.error("User already exists. Try a different email or username.")
            else:
                st.error("Passwords do not match!")

    elif choice == "Login":
        st.subheader("Login to Your Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if login_user(email, password):
                st.success("Login Successful!")
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Invalid email or password.")
else:
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()
    
    # Load model
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(32, (3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(15, activation='softmax')
    ])

    model.load_weights('model/model_weights.h5')

    # List of plant diseases
    plants = ['Pepper_bell_Bacterial_spot', 'Pepperbell_healthy', 'Potato_Early_blight',
              'Potato_Bacterial_wilt', 'Cucumber_mosaic_virus',
              'Potato__Late_blight', 'Tomato_Bacterial_spot',
              'Tomato_Early_blight', 'Tomato_healthy', 'Tomato_Late_blight',
              'Tomato_Leaf_Mold', 'Tomato_Septoria_leaf_spot',
              'Tomato_Spider_mites_Two_spotted_spider_mite', 'Tomato_Target_Spot',
              'Tomato_mosaic_virus', 'Tomato_YellowLeaf_Curl_Virus']

    precautions = {
        'Pepper_bell_Bacterial_spot': [
        'Remove and destroy infected plants.',
        'Avoid overhead watering to reduce leaf moisture.',
        'Use copper-based bactericides as a preventive measure.'
    ],
    'Tomato_Leaf_Mold':[
        'Maintain good air circulation by spacing plants properly.',
        'Avoid excessive humidity by ensuring proper ventilation in greenhouses.',
        'Water plants at the base, not overhead, to reduce leaf wetness.'
    ],
    'Tomato_Bacterial_spot': [
        'Practice crop rotation to reduce bacterial populations.',
        'Avoid working in the garden when plants are wet.',
        'Use disease-free seeds and resistant plant varieties.'
    ],
    'Potato_Bacterial_wilt': [
        'Avoid planting in previously infected soils.',
        'Ensure proper drainage to prevent waterlogging.',
        'Sanitize tools and avoid damage to tubers during harvesting.'
    ],
    'Tomato_mosaic_virus': [
        'Remove and destroy infected plants immediately.',
        'Disinfect tools and wash hands thoroughly after handling plants.',
        'Control insect vectors such as aphids and whiteflies.'
    ],
    'Cucumber_mosaic_virus': [
        'Use virus-free seeds and resistant varieties.',
        'Control aphids with insecticidal soaps or natural predators.',
        'Remove weeds that can host the virus.'
    ],
        'Tomato_Late_blight': [
        'Avoid overhead watering and ensure good air circulation.',
        'Apply fungicides as a preventive measure.',
        'Remove and destroy infected leaves or plants.'
    ],
    'Potato_Early_blight': [
        'Practice crop rotation and avoid planting potatoes in the same soil consecutively.',
        'Remove and dispose of plant debris properly.',
        'Apply fungicides during periods of high humidity.'
    ],
        'Tomato_Early_blight': [
        'Practice crop rotation and avoid planting potatoes in the same soil consecutively.',
        'Remove and dispose of plant debris properly.',
        'Apply fungicides during periods of high humidity.'
    ],
    'Tomato_Septoria_leaf_spot': [
        'Water at the base of the plant to keep foliage dry.',
        'Space plants properly to improve airflow.',
        'Remove and destroy infected leaves.'
    ],
    'Potato__Late_blight': [
        'Avoid overhead irrigation, especially in the evening, to keep leaves dry.',
        'Ensure proper spacing between plants for good airflow.',
        'Remove and destroy infected plants immediately.'
    ],
    'Tomato_Target_Spot':[
        'Remove infected leaves. Improve air circulation.',
        'Avoid overhead watering. Water at the base.',
        'Use disease-resistant tomato varieties. Apply mulch.'
    ],
    'Tomato_healthy': ['No action needed. Plant is healthy!'],
    'Pepperbell_healthy': ['No action needed. Plant is healthy!'],
    }




    # Upload Image
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        img_resized = cv2.resize(img, (64, 64))
        
        st.image(img, caption='Uploaded Image', use_container_width=True)
        
        img_resized = np.array(img_resized).reshape(1, 64, 64, 3).astype('float32') / 255.0
        preds = model.predict(img_resized)
        predict = np.argmax(preds)
        predicted_disease = plants[predict]
        
        st.success(f"*Predicted Disease:* {predicted_disease}")
        
        st.write("### Precautions:")
        for step in precautions.get(predicted_disease, ["No specific precautions available."]):
            st.write(f"- {step}")


        