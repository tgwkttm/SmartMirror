import tkinter as tk
import json
import os
from welcome_window import WelcomeWindow
from login_options_window import LoginOptionsWindow
from new_user_window import NewUserWindow
from existing_user_window import ExistingUserLoginWindow
from user_options_window import UserOptionsWindow  
import firebase_admin
from firebase_admin import credentials
from session_manager import save_session, load_session, clear_session

# Initialize Firebase only once
cred = credentials.Certificate("firebase_config.json")
try:
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'smartmirror-c6c98.appspot.com'
    })
except ValueError:
    print("Firebase app already initialized")

class MainApplication:
    def __init__(self, root): 
        print("MainApplication started")  
        self.root = root
        self.current_window = None

        #verify if there's a saved session
        user_session = load_session()
        
        if user_session:
            print("[INFO] Session found! Automatic Authentication...")
            self.open_user_options_window(user_session)  #login automat
        else:
            print("[INFO] No session found. Open Welcome Window.")
            self.open_welcome_window()  #if it doesn't exist, Welcome window is opened

    def open_welcome_window(self):
        """Open Welcome Window"""
        self.clear_window()
        self.current_window = WelcomeWindow(self.root, self)

    def open_login_options_window(self):
        """Open Login Options"""
        self.clear_window()
        self.current_window = LoginOptionsWindow(self.root, self)

    def open_new_user_window(self):
        """Open the window for creating a new account"""
        self.clear_window()
        self.current_window = NewUserWindow(self.root, self)

    def open_existing_user_window(self):
        """Open the login window for existing users"""
        self.clear_window()
        self.current_window = ExistingUserLoginWindow(self.root, self)  

    def open_user_options_window(self, user_data):
        """Open user options and save the session"""
        self.clear_window()
        self.current_window = UserOptionsWindow(self.root, user_data, self)
        save_session(user_data)  #salvez sesiunea utilizatorului

    def clear_window(self):
        """Clean the window before opening a new one"""
        if self.current_window is not None:
            if self.root.winfo_exists():
                for widget in self.root.winfo_children():
                    widget.destroy()
            self.current_window = None

    def close(self):
        """Close app"""
        self.root.quit()

if __name__ == "__main__":  # 🔴 Corectat __name_
    root = tk.Tk()
    app = MainApplication(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()