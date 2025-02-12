import tkinter as tk
from datetime import datetime

class WelcomeWindow:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app

        # Set the window title
        self.root.title("SmartReact")

        # Set window background color to black
        self.root.configure(bg="black")

        # Label for welcome message
        self.label_welcome = tk.Label(root, text="Welcome to SmartReact", font=("Helvetica", 24), fg="white", bg="black")
        self.label_welcome.pack(pady=20)

        # Label for current date and time
        self.label_datetime = tk.Label(root, text=self.get_current_datetime(), font=("Helvetica", 16), fg="white", bg="black")
        self.label_datetime.pack(pady=20)

        # Button for Login
        self.button_login = tk.Button(root, text="Login", command=self.main_app.open_login_options_window, bg="grey", fg="white")
        self.button_login.pack(pady=10)

    def get_current_datetime(self):
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    class MainApp:
        def open_login_options_window(self):
            print("Login button clicked")

        def open_new_user_window(self):
            print("Register button clicked")

    root = tk.Tk()
    app = WelcomeWindow(root, MainApp())
    root.mainloop()
