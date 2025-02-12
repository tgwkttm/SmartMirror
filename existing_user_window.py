import tkinter as tk
from tkinter import messagebox
from notes import NotesApp
from emotion_detector_app import EmotionDetectorApp
from calendar_app import CalendarApp
from facial_recognition import FaceLogin
import requests
import firebase_admin
from firebase_admin import firestore
import threading
import time
from arduino_module import init_serial, read_data, close_serial
import json

#initialize Firebase Firestore if not already initialized
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

class ExistingUserLoginWindow:
    def __init__(self, root, main_app): 
        self.root = root
        self.main_app = main_app  #reference to the main application
        self.root.title("Existing User Login")

        #frame for login form
        self.login_frame = tk.Frame(self.root, bg='black')
        self.login_frame.pack(padx=20, pady=20)

        #labels and fields for email and password
        tk.Label(self.login_frame, text="Email:", bg='black', fg='white').grid(row=0, column=0, sticky="w")
        self.email_entry = tk.Entry(self.login_frame)
        self.email_entry.grid(row=0, column=1)

        tk.Label(self.login_frame, text="Password:", bg='black', fg='white').grid(row=1, column=0, sticky="w")
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)

        #button for login
        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login_user)
        self.login_button.grid(row=2, columnspan=2, pady=10)

        #button for Face Login
        self.face_login_button = tk.Button(self.login_frame, text="Face Login", command=self.open_face_login, bg='gray', fg='white')
        self.face_login_button.grid(row=3, columnspan=2, pady=10)
    
    def save_session(self, user_data):
        """Saves user session to a JSON file."""
        try:
            with open("session.json", "w") as file:
                json.dump(user_data, file)
            print("[INFO] User session has been saved!")
        except Exception as e:
            print(f"[ERROR] Failed to save session: {e}")
    
    def login_user(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyAgLz3RD7F9qef2jDIrlCeouOuQHrGdRlI"

        data = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        response = requests.post(url, json=data)
        response_data = response.json()

        if response.status_code == 200:
            uid = response_data.get("localId")

            #search for user's name in Firestore
            user_ref = db.collection("users").document(uid).get()
            user_data = user_ref.to_dict()

            if user_data:
                name = user_data.get("name", "User")  # If "name" does not exist, use "User"
            else:
                name = "User"

            #update self.user_data
            self.user_data = {
                "uid": uid,
                "email": email,
                "name": name  # ✅ Now includes name!
            }
            
            self.save_session(self.user_data) 

            messagebox.showinfo("Login Successful", f"Successfully logged in as {name}")
            self.clear_login_fields()
            self.open_user_options()

        else:
            error_message = response_data.get("error", {}).get("message", "Unknown error")
            messagebox.showerror("Login Error", f"Failed to login: {error_message}")

    def open_face_login(self):
        """Authenticate user via facial recognition."""

        if hasattr(self, "face_login") and self.face_login:
            try:
                self.face_login.camera.close()
                del self.face_login
                time.sleep(1)
            except Exception as e:
                print(f"Error releasing camera: {e}")

        try:
            self.face_login = FaceLogin()
            user_id = self.face_login.authenticate()

            if user_id:
                user_ref = db.collection("users").document(user_id).get()
                if user_ref.exists:
                    user_data = user_ref.to_dict()
                    user_name = user_data.get("displayName") or user_data.get("name", "Unknown User")
                    self.user_data = {"uid": user_id, "name": user_name}
                    
                    self.save_session(self.user_data) 
                    
                    messagebox.showinfo("Login Successful", f"Face Login successful for {user_name}")
                    self.open_user_options()
                else:
                    messagebox.showerror("Login Failed", "User data not found.")
            else:
                messagebox.showerror("Face Login Failed", "No matching face found.")

        except Exception as e:
            messagebox.showerror("Camera Error", f"Camera initialization failed: {str(e)}")
            
    def clear_login_fields(self):
        """Clears login fields after authentication."""
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
    
    def open_user_options(self):
        """Hides the login window and opens User Options in a new window."""

        #create a new window for User Options
        user_options_root = tk.Toplevel(self.root)
        user_options_root.configure(bg='black')
        user_options_root.attributes('-fullscreen', True)

        #initialize User Options correctly (ONLY 2 arguments)
        from user_options_window import UserOptionsWindow
        user_options = UserOptionsWindow(user_options_root, self.user_data, self.main_app)

        print("[INFO] User Options opened in a new window.")