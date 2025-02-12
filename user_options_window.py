import tkinter as tk
from tkinter import messagebox
from notes import NotesApp
from emotion_detector_app import EmotionDetectorApp
from calendar_app import CalendarApp
import threading
import time
from arduino_module import init_serial, read_data, close_serial
import json
import re
import requests
import os
from session_manager import clear_session, logout_from_firebase

class UserOptionsWindow:
    def __init__(self, root, user_data, main_app):
        self.root = root
        self.user_data = user_data
        self.root.title("User Options")
        self.root.configure(bg='black')
        self.root.attributes('-fullscreen', True)  #fullscreen enabled
        self.main_app = main_app

        greeting_label = tk.Label(self.root, text=f"Hello, {self.user_data['name']}!", font=("Helvetica", 24), bg='black', fg='white')
        greeting_label.pack(side=tk.TOP, pady=20)

        #labels for sensor data
        self.air_quality_label = tk.Label(
            self.root, 
            text="Air Quality: Waiting for sensor...\n"
                 "CO₂: -- ppm\n"
                 "NH₃: -- ppm\n"
                 "Benzen: -- ppm\n"
                 "Alcohol: -- ppm\n"
                 "NOx: -- ppm\n"
                 "Temperature: -- °C\n"
                 "Humidity: -- %",
            font=("Helvetica", 14), 
            bg='black', 
            fg='white', 
            anchor='w'
        )

        self.air_quality_label.pack(pady=10, anchor='w')
        
        self.warning_label = tk.Label(self.root, text="", font=("Helvetica", 14, "bold"), bg='black', fg='red', anchor='w')
        self.warning_label.pack(pady=10, anchor='w')

        # Frame for buttons positioned vertically on the right
        user_options_frame = tk.Frame(self.root, bg='black')
        user_options_frame.pack(side=tk.RIGHT, padx=50, pady=50, anchor="e")

        # Buttons
        calendar_button = tk.Button(user_options_frame, text="Calendar", command=self.open_calendar, font=("Helvetica", 18))
        calendar_button.pack(pady=10, fill=tk.X)

        notes_button = tk.Button(user_options_frame, text="Notes", command=self.open_notes, font=("Helvetica", 18))
        notes_button.pack(pady=10, fill=tk.X)

        emotion_button = tk.Button(user_options_frame, text="Emotion Detection", command=self.open_emotion_detection, font=("Helvetica", 18))
        emotion_button.pack(pady=10, fill=tk.X)

        logout_button = tk.Button(user_options_frame, text="Log Out", command=self.logout, font=("Helvetica", 18), bg="red", fg="white")
        logout_button.pack(pady=10, fill=tk.X)

        delete_button = tk.Button(user_options_frame, text="Delete User", command=self.delete_user, font=("Helvetica", 18), bg="darkred", fg="white")
        delete_button.pack(pady=10, fill=tk.X)

        # Initialize serial connection with Arduino
        self.serial_connection = init_serial('/dev/ttyUSB0')

        if self.serial_connection:
            self.read_data_thread = threading.Thread(target=self.read_arduino_data)
            self.read_data_thread.daemon = True
            self.read_data_thread.start()
        else:
            self.air_quality_label.config(text="No Sensor Detected")

    def read_arduino_data(self):
        """Read data from Arduino and update UI."""
        while self.serial_connection:
            data = read_data(self.serial_connection)
            if data:
                print(f"Sensor Data: {data}")
                self.root.after(100, lambda: self.update_air_quality(data))
            time.sleep(1)

    def update_air_quality(self, data):
        if not self.root.winfo_exists():
            print("[WARNING] Window closed, stopping updates.")
            return

        match = re.search(
            r'CO2: (\d+\.?\d*) ppm \| NH3: (\d+\.?\d*) ppm \| Benzen: (\d+\.?\d*) ppm \| '
            r'Alcohol: (\d+\.?\d*) ppm \| NOx: (\d+\.?\d*) ppm \| Temp: (\d+\.?\d*)°C \| '
            r'Humidity: (\d+\.?\d*)% \| AQI: (\d+)', 
            data
        )

        if match:
            co2, nh3, benzen, alcohol, nox, temperature, humidity, aqi = match.groups()

            self.air_quality_label.config(
                text=f"Air Quality: {aqi} (AQI)\n"
                     f"CO₂: {co2} ppm\n"
                     f"NH₃: {nh3} ppm\n"
                     f"Benzen: {benzen} ppm\n"
                     f"Alcohol: {alcohol} ppm\n"
                     f"NOx: {nox} ppm\n"
                     f"Temperature: {temperature}°C\n"
                     f"Humidity: {humidity}%"
            )

    def logout(self):
        """Log out the user and return to the login screen."""
        print("[INFO] Logging out...")
        logout_from_firebase()
        
        #inchide conexiunea serială dacă este activă
        if self.serial_connection:
            close_serial(self.serial_connection)
            self.serial_connection = None
            print("[INFO] Serial connection closed.")

        #oprește thread-ul de citire a senzorilor
        self.is_detection_running = False  #dacă există un flag care controlează loop-ul
        print("[INFO] Stopping sensor data thread...")

        #arată un mesaj de confirmare
        messagebox.showinfo("Logged Out", "You have been logged out successfully.")

        #inchide fereastra actuală și deschide ecranul de login
        self.root.destroy()
        self.main_app.open_existing_user_window()
        self.root.withdraw()
        print("[INFO] User Options window hidden!")
        self.main_app.open_existing_user_window()

    def delete_user(self):
        """Delete the current user's account."""
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete your account?")
        if not confirm:
            self.root.lift()
            self.root.focus_force()
            return

        try:
            user_ref = db.collection("users").document(self.user_data["uid"])
            user_ref.delete()
            messagebox.showinfo("Account Deleted", "Your account has been successfully deleted.")
            self.logout()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete account: {str(e)}")

    def open_calendar(self):
        """Open Calendar App."""
        calendar_root = tk.Toplevel(self.root)
        CalendarApp(calendar_root, self.user_data)

    def open_notes(self):
        """Open Notes App."""
        notes_root = tk.Toplevel(self.root)
        NotesApp(notes_root, self.user_data)

    def open_emotion_detection(self):
        """Open Emotion Detection App."""
        emotion_root = tk.Toplevel(self.root)
        EmotionDetectorApp(emotion_root)