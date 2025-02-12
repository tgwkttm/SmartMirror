import tkinter as tk
from tkinter import messagebox
import os
import time
import cv2  #openCV for face detection
import re  #module for password validation
from firebase_config import db, bucket
from picamera2 import Picamera2
import firebase_user_manager
from facial_recognition_utils import add_images_to_encodings  # Utility for encodings

class NewUserWindow:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app

        self.root.title("Register New User")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", self.exit_fullscreen)

        # Registration form frame
        self.registration_frame = tk.Frame(self.root, bg="black")
        self.registration_frame.pack(padx=20, pady=20)

        # Fields for name, email, and password
        tk.Label(self.registration_frame, text="Name:", bg="black", fg="white", font=("Helvetica", 14)).grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(self.registration_frame, font=("Helvetica", 14))
        self.name_entry.grid(row=0, column=1, pady=5)

        tk.Label(self.registration_frame, text="Email:", bg="black", fg="white", font=("Helvetica", 14)).grid(row=1, column=0, sticky="w")
        self.email_entry = tk.Entry(self.registration_frame, font=("Helvetica", 14))
        self.email_entry.grid(row=1, column=1, pady=5)

        tk.Label(self.registration_frame, text="Password:", bg="black", fg="white", font=("Helvetica", 14)).grid(row=2, column=0, sticky="w")
        self.password_entry = tk.Entry(self.registration_frame, show="*", font=("Helvetica", 14))
        self.password_entry.grid(row=2, column=1, pady=5)

        # Button to start face registration
        self.register_button = tk.Button(self.registration_frame, text="Start Face Registration", command=self.register_user, bg="grey", fg="white", font=("Helvetica", 14))
        self.register_button.grid(row=3, columnspan=2, pady=10)

    def is_valid_password(self, password):
        """Verify password security rules"""
        if len(password) < 8:
            return "Password must be at least 8 characters long."
        if not re.search(r"[A-Z]", password):
            return "Password must contain at least one uppercase letter."
        if not re.search(r"[a-z]", password):
            return "Password must contain at least one lowercase letter."
        if not re.search(r"\d", password):
            return "Password must contain at least one number."
        if not re.search(r"[!@#$%^&*()_+={}\[\]:;<>,.?/~\\-]", password):
            return "Password must contain at least one special character (!@#$%^&* etc.)."
        return None  # Password is valid

    def is_email_registered(self, email):
        """Check if the email is already registered in Firebase."""
        users_ref = db.collection("users").where("email", "==", email).get()
        return len(users_ref) > 0

    def register_user(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not name or not email or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        #check if the email is already registered
        if self.is_email_registered(email):
            messagebox.showerror("Error", "This email is already in use.")
            return

        #validate password
        password_error = self.is_valid_password(password)
        if password_error:
            messagebox.showerror("Invalid Password", password_error)
            return

        user_uid = firebase_user_manager.create_and_store_user(name, email, password)
        if not user_uid:
            messagebox.showerror("Error", "Error creating user.")
            return

        #create directory for images
        user_directory = os.path.join("dataset", user_uid)
        os.makedirs(user_directory, exist_ok=True)

        messagebox.showinfo("Starting Capture", "Image capture for face detection is about to start.")

        image_urls = self.capture_images(user_directory, user_uid)
        firebase_user_manager.link_images_to_user(user_uid, image_urls)
        
        firebase_user_manager.update_encodings()

        messagebox.showinfo("Success", "User successfully created! You can now log in.")
        self.root.destroy()

    def capture_images(self, user_directory, username):
        camera = Picamera2()
        config = camera.create_still_configuration(main={"size": (1024, 768)})
        camera.configure(config)
        camera.start()
        time.sleep(2)

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        captured_images = 0
        image_urls = []

        try:
            while captured_images < 10:
                frame = camera.capture_array()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(50, 50))

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                cv2.imshow("Position Your Face Correctly", frame)

                if len(faces) > 0:
                    img_name = f"image_{captured_images}.jpg"
                    img_path = os.path.join(user_directory, img_name)
                    cv2.imwrite(img_path, frame)
                    storage_path = f"images/{username}/{img_name}"
                    image_url = firebase_user_manager.upload_image_to_storage(img_path, storage_path)
                    if image_url:
                        image_urls.append(image_url)
                    captured_images += 1

                if cv2.waitKey(500) & 0xFF == ord("q"):
                    break

        finally:
            camera.stop()
            cv2.destroyAllWindows()

        if captured_images < 5:
            messagebox.showerror("Error", "Not enough images captured. Please try again.")
            return []

        #add new images to encodings.pickle
        add_images_to_encodings(user_directory, username)

        messagebox.showinfo("Capture Completed", "Image capture successfully completed!")
        self.main_app.open_login_options_window()
        return image_urls

    def exit_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", False)

if __name__ == "__main__":
    class MainApp:
        def open_login_options_window(self):
            print("Login options window should open now.")

    root = tk.Tk()
    app = NewUserWindow(root, MainApp())
    root.mainloop()